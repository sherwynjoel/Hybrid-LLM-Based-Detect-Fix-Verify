package com.hybridllm.actions;

import com.intellij.openapi.actionSystem.AnAction;
import com.intellij.openapi.actionSystem.AnActionEvent;
import com.intellij.openapi.project.Project;
import com.intellij.openapi.ui.Messages;
import org.jetbrains.annotations.NotNull;

public class TogglePrivacyModeAction extends AnAction {
    private static boolean privacyFirstMode = true;

    @Override
    public void actionPerformed(@NotNull AnActionEvent e) {
        privacyFirstMode = !privacyFirstMode;
        String mode = privacyFirstMode ? "Privacy-First" : "Efficiency";
        Messages.showInfoMessage(
            "Switched to " + mode + " mode\n\n" +
            (privacyFirstMode 
                ? "Sensitive code → Local LLM\nNormal code → Cloud LLM"
                : "Using efficiency-based routing"),
            "Privacy Mode Changed"
        );
    }

    @Override
    public void update(@NotNull AnActionEvent e) {
        e.getPresentation().setText(
            privacyFirstMode ? "Disable Privacy-First Mode" : "Enable Privacy-First Mode"
        );
    }

    public static boolean isPrivacyFirstMode() {
        return privacyFirstMode;
    }
}


