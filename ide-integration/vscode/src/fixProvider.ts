import * as vscode from 'vscode';
import axios from 'axios';
import { VulnerabilityAnalyzer, Vulnerability } from './analyzer';

export class FixProvider implements vscode.CodeActionProvider {
    private apiUrl: string;

    constructor(private analyzer: VulnerabilityAnalyzer) {
        const config = vscode.workspace.getConfiguration('hybridLLM');
        this.apiUrl = config.get('apiUrl', 'http://localhost:8501/api') as string;
    }

    provideCodeActions(
        document: vscode.TextDocument,
        range: vscode.Range,
        context: vscode.CodeActionContext,
        token: vscode.CancellationToken
    ): vscode.CodeAction[] | undefined {
        const actions: vscode.CodeAction[] = [];

        for (const diagnostic of context.diagnostics) {
            if (diagnostic.source !== 'Hybrid LLM') {
                continue;
            }

            const vulnerability = (diagnostic as any).vulnerability as Vulnerability;
            if (!vulnerability) {
                continue;
            }

            // Quick fix action
            const fixAction = new vscode.CodeAction(
                `Fix ${vulnerability.type}`,
                vscode.CodeActionKind.QuickFix
            );
            fixAction.diagnostics = [diagnostic];
            fixAction.command = {
                command: 'hybridLLM.fixVulnerability',
                title: `Fix ${vulnerability.type}`,
                arguments: [vulnerability, document, diagnostic]
            };
            actions.push(fixAction);

            // Show details action
            const detailsAction = new vscode.CodeAction(
                `Show ${vulnerability.type} details`,
                vscode.CodeActionKind.Empty
            );
            detailsAction.command = {
                command: 'hybridLLM.showVulnerabilityDetails',
                title: 'Show vulnerability details',
                arguments: [vulnerability]
            };
            actions.push(detailsAction);
        }

        return actions.length > 0 ? actions : undefined;
    }

    async fixVulnerability(
        vulnerability: Vulnerability,
        document: vscode.TextDocument,
        diagnostic: vscode.Diagnostic
    ): Promise<void> {
        try {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: `Fixing ${vulnerability.type}...`,
                cancellable: false
            }, async (progress: vscode.Progress<{ message?: string; increment?: number }>) => {
                const code = document.getText();
                const language = this.mapLanguageId(document.languageId);

                // Call framework API for fix
                const response = await axios.post(`${this.apiUrl}/fix`, {
                    code: code,
                    vulnerability: vulnerability,
                    language: language
                }, {
                    timeout: 60000
                });

                const fixedCode = response.data.fixed_code;
                if (!fixedCode) {
                    vscode.window.showErrorMessage('Fix generation failed');
                    return;
                }

                // Apply fix
                const config = vscode.workspace.getConfiguration('hybridLLM');
                const autoFix = config.get('autoFix', false);

                if (autoFix) {
                    // Auto-apply fix
                    const edit = new vscode.WorkspaceEdit();
                    const fullRange = new vscode.Range(
                        document.positionAt(0),
                        document.positionAt(code.length)
                    );
                    edit.replace(document.uri, fullRange, fixedCode);
                    await vscode.workspace.applyEdit(edit);
                    vscode.window.showInformationMessage('Fix applied successfully!');
                } else {
                    // Show fix in diff view
                    const tempUri = vscode.Uri.parse(`hybrid-llm-fix:${document.fileName}`);
                    await vscode.workspace.fs.writeFile(
                        tempUri,
                        Buffer.from(fixedCode, 'utf8')
                    );
                    await vscode.commands.executeCommand(
                        'vscode.diff',
                        document.uri,
                        tempUri,
                        `Fix for ${vulnerability.type}`
                    );
                }
            });
        } catch (error: any) {
            console.error('Fix error:', error);
            vscode.window.showErrorMessage(`Failed to fix vulnerability: ${error.message}`);
        }
    }

    private mapLanguageId(languageId: string): string {
        const mapping: { [key: string]: string } = {
            'python': 'python',
            'javascript': 'javascript',
            'typescript': 'typescript',
            'java': 'java',
            'cpp': 'cpp',
            'c': 'c'
        };
        return mapping[languageId] || 'python';
    }
}

