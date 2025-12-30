package com.hybridllm.actions;

import com.intellij.openapi.actionSystem.AnAction;
import com.intellij.openapi.actionSystem.AnActionEvent;
import com.intellij.openapi.actionSystem.CommonDataKeys;
import com.intellij.openapi.progress.ProgressIndicator;
import com.intellij.openapi.progress.ProgressManager;
import com.intellij.openapi.progress.Task;
import com.intellij.openapi.project.Project;
import com.intellij.openapi.ui.Messages;
import com.intellij.openapi.vfs.VirtualFile;
import com.hybridllm.api.FrameworkClient;
import com.hybridllm.model.VulnerabilityResult;
import org.jetbrains.annotations.NotNull;

public class AnalyzeFileAction extends AnAction {
    @Override
    public void actionPerformed(@NotNull AnActionEvent e) {
        Project project = e.getProject();
        VirtualFile file = e.getData(CommonDataKeys.VIRTUAL_FILE);
        
        if (file == null || project == null) {
            Messages.showErrorDialog("Please select a file to analyze", "No File Selected");
            return;
        }
        
        ProgressManager.getInstance().run(new Task.Backgroundable(project, "Analyzing for vulnerabilities...") {
            @Override
            public void run(@NotNull ProgressIndicator indicator) {
                try {
                    indicator.setText("Analyzing " + file.getName() + "...");
                    
                    FrameworkClient client = new FrameworkClient();
                    boolean privacyMode = com.hybridllm.actions.TogglePrivacyModeAction.isPrivacyFirstMode();
                    VulnerabilityResult result = client.analyzeFile(file.getPath(), privacyMode);
                    
                    if (result.hasVulnerabilities()) {
                        Messages.showInfoMessage(
                            "Found " + result.getVulnerabilityCount() + " vulnerabilities",
                            "Analysis Complete"
                        );
                        // Show results in tool window
                        com.hybridllm.ui.ResultToolWindow.showResults(project, result);
                    } else {
                        Messages.showInfoMessage("No vulnerabilities found!", "Analysis Complete");
                    }
                } catch (Exception ex) {
                    Messages.showErrorDialog(
                        "Analysis failed: " + ex.getMessage(),
                        "Analysis Error"
                    );
                }
            }
        });
    }
    
    @Override
    public void update(@NotNull AnActionEvent e) {
        VirtualFile file = e.getData(CommonDataKeys.VIRTUAL_FILE);
        e.getPresentation().setEnabled(file != null && isSupportedFile(file));
    }
    
    private boolean isSupportedFile(VirtualFile file) {
        String extension = file.getExtension();
        return extension != null && (
            extension.equals("py") ||
            extension.equals("java") ||
            extension.equals("js") ||
            extension.equals("ts") ||
            extension.equals("cpp") ||
            extension.equals("c")
        );
    }
}


