package com.hybridllm.ui;

import com.intellij.openapi.project.Project;
import com.intellij.openapi.wm.ToolWindow;
import com.intellij.openapi.wm.ToolWindowFactory;
import com.intellij.ui.content.Content;
import com.intellij.ui.content.ContentFactory;
import com.hybridllm.model.VulnerabilityResult;
import org.jetbrains.annotations.NotNull;

import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.util.List;

public class ResultToolWindow implements ToolWindowFactory {
    private static JTable vulnerabilityTable;
    private static DefaultTableModel tableModel;

    @Override
    public void createToolWindowContent(@NotNull Project project, @NotNull ToolWindow toolWindow) {
        JPanel panel = new JPanel(new BorderLayout());
        
        // Create table
        String[] columns = {"Line", "Type", "Severity", "CWE", "Message"};
        tableModel = new DefaultTableModel(columns, 0) {
            @Override
            public boolean isCellEditable(int row, int column) {
                return false;
            }
        };
        vulnerabilityTable = new JTable(tableModel);
        vulnerabilityTable.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
        
        JScrollPane scrollPane = new JScrollPane(vulnerabilityTable);
        panel.add(scrollPane, BorderLayout.CENTER);
        
        // Add summary label
        JLabel summaryLabel = new JLabel("No vulnerabilities found");
        summaryLabel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));
        panel.add(summaryLabel, BorderLayout.NORTH);
        
        Content content = ContentFactory.SERVICE.getInstance().createContent(panel, "", false);
        toolWindow.getContentManager().addContent(content);
    }

    public static void showResults(@NotNull Project project, @NotNull VulnerabilityResult result) {
        if (tableModel == null) {
            // Tool window not initialized yet
            return;
        }

        // Clear existing data
        tableModel.setRowCount(0);

        // Add vulnerabilities
        List<com.hybridllm.model.Vulnerability> vulnerabilities = result.getVulnerabilities();
        for (com.hybridllm.model.Vulnerability vuln : vulnerabilities) {
            Object[] row = {
                vuln.getLine(),
                vuln.getType(),
                vuln.getSeverity(),
                vuln.getCwe() != null ? vuln.getCwe() : "N/A",
                vuln.getMessage()
            };
            tableModel.addRow(row);
        }
    }
}


