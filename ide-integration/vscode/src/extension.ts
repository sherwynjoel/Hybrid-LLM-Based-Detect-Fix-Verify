import * as vscode from 'vscode';
import { VulnerabilityAnalyzer } from './analyzer';
import { FixProvider } from './fixProvider';
import { ReportPanel } from './reportPanel';

let analyzer: VulnerabilityAnalyzer;
let fixProvider: FixProvider;
let diagnosticCollection: vscode.DiagnosticCollection;

export function activate(context: vscode.ExtensionContext) {
    console.log('Hybrid LLM Vulnerability Repair extension is now active!');

    // Initialize components
    diagnosticCollection = vscode.languages.createDiagnosticCollection('hybridLLM');
    analyzer = new VulnerabilityAnalyzer(diagnosticCollection);
    fixProvider = new FixProvider(analyzer);

    // Register commands
    const analyzeFileCommand = vscode.commands.registerCommand(
        'hybridLLM.analyzeFile',
        () => analyzeCurrentFile(analyzer)
    );

    const analyzeWorkspaceCommand = vscode.commands.registerCommand(
        'hybridLLM.analyzeWorkspace',
        () => analyzeWorkspace(analyzer)
    );

    const fixVulnerabilityCommand = vscode.commands.registerCommand(
        'hybridLLM.fixVulnerability',
        (vulnerability: any, document?: vscode.TextDocument, diagnostic?: vscode.Diagnostic) => {
            if (vulnerability && document && diagnostic) {
                fixProvider.fixVulnerability(vulnerability, document, diagnostic);
            } else if (vulnerability) {
                // Fallback: try to get current document
                const editor = vscode.window.activeTextEditor;
                if (editor) {
                    fixProvider.fixVulnerability(vulnerability, editor.document, diagnostic || null);
                }
            }
        }
    );

    const togglePrivacyCommand = vscode.commands.registerCommand(
        'hybridLLM.togglePrivacyMode',
        () => togglePrivacyMode()
    );

    const showReportCommand = vscode.commands.registerCommand(
        'hybridLLM.showReport',
        () => ReportPanel.createOrShow(context.extensionUri)
    );

    // Register code actions
    const codeActionProvider = vscode.languages.registerCodeActionsProvider(
        { scheme: 'file', language: 'python' },
        fixProvider,
        {
            providedCodeActionKinds: [vscode.CodeActionKind.QuickFix]
        }
    );

    // Auto-analyze on file save
    const onSave = vscode.workspace.onDidSaveTextDocument((document: vscode.TextDocument) => {
        const config = vscode.workspace.getConfiguration('hybridLLM');
        if (config.get('enable', true) && isSupportedLanguage(document.languageId)) {
            analyzer.analyzeDocument(document);
        }
    });

    // Auto-analyze on file open
    const onOpen = vscode.workspace.onDidOpenTextDocument((document: vscode.TextDocument) => {
        const config = vscode.workspace.getConfiguration('hybridLLM');
        if (config.get('enable', true) && isSupportedLanguage(document.languageId)) {
            analyzer.analyzeDocument(document);
        }
    });

    // Real-time analysis (debounced)
    let analysisTimer: NodeJS.Timeout | undefined;
    const onChange = vscode.workspace.onDidChangeTextDocument((event: vscode.TextDocumentChangeEvent) => {
        const config = vscode.workspace.getConfiguration('hybridLLM');
        if (config.get('enable', true) && isSupportedLanguage(event.document.languageId)) {
            // Debounce analysis
            if (analysisTimer) {
                clearTimeout(analysisTimer);
            }
            analysisTimer = setTimeout(() => {
                analyzer.analyzeDocument(event.document);
            }, 1000); // Wait 1 second after last change
        }
    });

    // Add to subscriptions
    context.subscriptions.push(
        analyzeFileCommand,
        analyzeWorkspaceCommand,
        fixVulnerabilityCommand,
        togglePrivacyCommand,
        showReportCommand,
        codeActionProvider,
        onSave,
        onOpen,
        onChange,
        diagnosticCollection
    );

    // Show welcome message
    vscode.window.showInformationMessage('Hybrid LLM Vulnerability Repair extension activated!');
}

function isSupportedLanguage(languageId: string): boolean {
    const supported = ['python', 'javascript', 'typescript', 'java', 'cpp', 'c'];
    return supported.includes(languageId);
}

async function analyzeCurrentFile(analyzer: VulnerabilityAnalyzer) {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showWarningMessage('No active editor');
        return;
    }

    vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: "Analyzing for vulnerabilities...",
        cancellable: false
    }, async (progress: vscode.Progress<{ message?: string; increment?: number }>) => {
        await analyzer.analyzeDocument(editor.document);
        vscode.window.showInformationMessage('Analysis complete!');
    });
}

async function analyzeWorkspace(analyzer: VulnerabilityAnalyzer) {
    const files = await vscode.workspace.findFiles(
        '**/*.{py,js,ts,java,cpp,c}',
        '**/node_modules/**'
    );

    vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: `Analyzing ${files.length} files...`,
        cancellable: true
    }, async (progress: vscode.Progress<{ message?: string; increment?: number }>, token: vscode.CancellationToken) => {
        for (let i = 0; i < files.length; i++) {
            if (token.isCancellationRequested) {
                break;
            }

            const document = await vscode.workspace.openTextDocument(files[i]);
            await analyzer.analyzeDocument(document);
            
            progress.report({
                increment: 100 / files.length,
                message: `Analyzing ${files[i].name}...`
            });
        }
        vscode.window.showInformationMessage(`Analysis complete! Analyzed ${files.length} files.`);
    });
}

async function togglePrivacyMode() {
    const config = vscode.workspace.getConfiguration('hybridLLM');
    const current = config.get('privacyFirstMode', true);
    await config.update('privacyFirstMode', !current, vscode.ConfigurationTarget.Global);
    
    const mode = !current ? 'Privacy-First' : 'Efficiency';
    vscode.window.showInformationMessage(`Switched to ${mode} mode`);
}

export function deactivate() {
    if (diagnosticCollection) {
        diagnosticCollection.dispose();
    }
}

