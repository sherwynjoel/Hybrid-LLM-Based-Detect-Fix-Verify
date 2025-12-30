package com.hybridllm.actions;

import com.intellij.openapi.actionSystem.AnAction;
import com.intellij.openapi.actionSystem.AnActionEvent;
import com.intellij.openapi.progress.ProgressIndicator;
import com.intellij.openapi.progress.ProgressManager;
import com.intellij.openapi.progress.Task;
import com.intellij.openapi.project.Project;
import com.intellij.openapi.ui.Messages;
import com.intellij.openapi.vfs.VirtualFile;
import com.hybridllm.api.FrameworkClient;
import com.hybridllm.model.VulnerabilityResult;
import org.jetbrains.annotations.NotNull;

import java.util.ArrayList;
import java.util.List;

public class AnalyzeProjectAction extends AnAction {
    @Override
    public void actionPerformed(@NotNull AnActionEvent e) {
        Project project = e.getProject();
        if (project == null) {
            Messages.showErrorDialog("No project selected", "Error");
            return;
        }

        VirtualFile baseDir = project.getBaseDir();
        if (baseDir == null) {
            Messages.showErrorDialog("Project base directory not found", "Error");
            return;
        }

        ProgressManager.getInstance().run(new Task.Backgroundable(project, "Analyzing project for vulnerabilities...") {
            @Override
            public void run(@NotNull ProgressIndicator indicator) {
                try {
                    List<VirtualFile> files = collectSourceFiles(baseDir, indicator);
                    FrameworkClient client = new FrameworkClient();
                    boolean privacyMode = TogglePrivacyModeAction.isPrivacyFirstMode();
                    int totalVulnerabilities = 0;
                    int filesAnalyzed = 0;

                    for (VirtualFile file : files) {
                        if (indicator.isCanceled()) break;
                        
                        indicator.setText("Analyzing " + file.getName() + "...");
                        indicator.setFraction((double) filesAnalyzed / files.size());

                        try {
                            VulnerabilityResult result = client.analyzeFile(file.getPath(), privacyMode);
                            totalVulnerabilities += result.getVulnerabilityCount();
                            filesAnalyzed++;
                        } catch (Exception ex) {
                            // Continue with next file
                        }
                    }

                    indicator.setFraction(1.0);
                    Messages.showInfoMessage(
                        String.format("Analysis complete!\nFiles analyzed: %d\nVulnerabilities found: %d",
                            filesAnalyzed, totalVulnerabilities),
                        "Project Analysis Complete"
                    );
                } catch (Exception ex) {
                    Messages.showErrorDialog(
                        "Analysis failed: " + ex.getMessage(),
                        "Analysis Error"
                    );
                }
            }
        });
    }

    private List<VirtualFile> collectSourceFiles(VirtualFile dir, ProgressIndicator indicator) {
        List<VirtualFile> files = new ArrayList<>();
        collectFilesRecursive(dir, files, indicator);
        return files;
    }

    private void collectFilesRecursive(VirtualFile dir, List<VirtualFile> files, ProgressIndicator indicator) {
        if (indicator.isCanceled()) return;

        VirtualFile[] children = dir.getChildren();
        for (VirtualFile child : children) {
            if (child.isDirectory()) {
                String name = child.getName();
                if (!name.equals("node_modules") && !name.equals(".git") && !name.equals("__pycache__")) {
                    collectFilesRecursive(child, files, indicator);
                }
            } else if (isSupportedFile(child)) {
                files.add(child);
            }
        }
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


