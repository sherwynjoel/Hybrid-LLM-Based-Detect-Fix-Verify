import * as vscode from 'vscode';
import axios from 'axios';

export interface Vulnerability {
    type: string;
    severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    line: number;
    column?: number;
    message: string;
    cwe?: string;
    code?: string;
    fix?: string;
}

export class VulnerabilityAnalyzer {
    private apiUrl: string;
    private privacyFirstMode: boolean;

    constructor(private diagnosticCollection: vscode.DiagnosticCollection) {
        const config = vscode.workspace.getConfiguration('hybridLLM');
        this.apiUrl = config.get('apiUrl', 'http://localhost:8501/api') as string;
        this.privacyFirstMode = config.get('privacyFirstMode', true) as boolean;
    }

    async analyzeDocument(document: vscode.TextDocument): Promise<void> {
        if (!this.isSupportedLanguage(document.languageId)) {
            return;
        }

        try {
            const code = document.getText();
            const language = this.mapLanguageId(document.languageId);

            // Call framework API
            const response = await axios.post(`${this.apiUrl}/analyze`, {
                code: code,
                language: language,
                privacy_first_mode: this.privacyFirstMode
            }, {
                timeout: 30000
            });

            const vulnerabilities = response.data.vulnerabilities || [];
            this.updateDiagnostics(document, vulnerabilities);

        } catch (error: any) {
            console.error('Analysis error:', error);
            if (error.code === 'ECONNREFUSED') {
                vscode.window.showErrorMessage(
                    'Cannot connect to Hybrid LLM Framework. Make sure the framework is running on ' + this.apiUrl
                );
            }
        }
    }

    private updateDiagnostics(document: vscode.TextDocument, vulnerabilities: Vulnerability[]): void {
        const diagnostics: vscode.Diagnostic[] = [];

        for (const vuln of vulnerabilities) {
            const line = Math.max(0, vuln.line - 1);
            const lineText = document.lineAt(line).text;
            const range = new vscode.Range(
                line,
                0,
                line,
                lineText.length
            );

            const diagnostic = new vscode.Diagnostic(
                range,
                `${vuln.type}: ${vuln.message}`,
                this.mapSeverity(vuln.severity)
            );

            diagnostic.source = 'Hybrid LLM';
            diagnostic.code = vuln.cwe || vuln.type;
            diagnostic.relatedInformation = [
                new vscode.DiagnosticRelatedInformation(
                    new vscode.Location(document.uri, range),
                    `CWE: ${vuln.cwe || 'N/A'}`
                )
            ];

            // Store vulnerability data for code actions
            (diagnostic as any).vulnerability = vuln;

            diagnostics.push(diagnostic);
        }

        this.diagnosticCollection.set(document.uri, diagnostics);
    }

    private mapSeverity(severity: string): vscode.DiagnosticSeverity {
        switch (severity.toUpperCase()) {
            case 'CRITICAL':
            case 'HIGH':
                return vscode.DiagnosticSeverity.Error;
            case 'MEDIUM':
                return vscode.DiagnosticSeverity.Warning;
            case 'LOW':
                return vscode.DiagnosticSeverity.Information;
            default:
                return vscode.DiagnosticSeverity.Warning;
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

    private isSupportedLanguage(languageId: string): boolean {
        return ['python', 'javascript', 'typescript', 'java', 'cpp', 'c'].includes(languageId);
    }
}


