import * as vscode from 'vscode';
import * as path from 'path';

export class ReportPanel {
    public static currentPanel: ReportPanel | undefined;
    public static readonly viewType = 'hybridLLMReport';
    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];

    public static createOrShow(extensionUri: vscode.Uri) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        if (ReportPanel.currentPanel) {
            ReportPanel.currentPanel._panel.reveal(column);
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            ReportPanel.viewType,
            'Vulnerability Report',
            column || vscode.ViewColumn.One,
            {
                enableScripts: true,
                localResourceRoots: [extensionUri]
            }
        );

        ReportPanel.currentPanel = new ReportPanel(panel, extensionUri);
    }

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this._panel = panel;
        this._panel.webview.html = this._getHtmlForWebview();
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
    }

    public dispose() {
        ReportPanel.currentPanel = undefined;
        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }

    private _getHtmlForWebview(): string {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Vulnerability Report</title>
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    padding: 20px;
                    color: var(--vscode-foreground);
                }
                .vulnerability {
                    border: 1px solid var(--vscode-panel-border);
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                }
                .severity-critical { border-left: 4px solid #f44336; }
                .severity-high { border-left: 4px solid #ff9800; }
                .severity-medium { border-left: 4px solid #ffc107; }
                .severity-low { border-left: 4px solid #4caf50; }
                .fix-button {
                    background: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    padding: 8px 16px;
                    cursor: pointer;
                    border-radius: 3px;
                }
            </style>
        </head>
        <body>
            <h1>🔒 Vulnerability Report</h1>
            <div id="report-content">
                <p>Run analysis to see vulnerabilities here.</p>
            </div>
        </body>
        </html>`;
    }
}


