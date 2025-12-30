package com.hybridllm.api;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import okhttp3.*;
import com.hybridllm.model.VulnerabilityResult;
import com.hybridllm.model.Vulnerability;
import org.jetbrains.annotations.NotNull;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class FrameworkClient {
    private static final String DEFAULT_API_URL = "http://localhost:8501/api";
    private final String apiUrl;
    private final OkHttpClient client;
    private final Gson gson;

    public FrameworkClient() {
        this(DEFAULT_API_URL);
    }

    public FrameworkClient(String apiUrl) {
        this.apiUrl = apiUrl;
        this.client = new OkHttpClient();
        this.gson = new Gson();
    }

    public VulnerabilityResult analyzeFile(@NotNull String filePath) throws IOException {
        return analyzeFile(filePath, false);
    }

    public VulnerabilityResult analyzeFile(@NotNull String filePath, boolean privacyFirstMode) throws IOException {
        // Read file content
        String code = java.nio.file.Files.readString(java.nio.file.Paths.get(filePath));
        
        // Determine language from file extension
        String language = getLanguageFromPath(filePath);
        
        // Call API
        JsonObject requestBody = new JsonObject();
        requestBody.addProperty("code", code);
        requestBody.addProperty("language", language);
        requestBody.addProperty("privacy_first_mode", privacyFirstMode);

        RequestBody body = RequestBody.create(
            requestBody.toString(),
            MediaType.parse("application/json")
        );

        Request request = new Request.Builder()
            .url(apiUrl + "/analyze")
            .post(body)
            .build();

        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new IOException("API call failed: " + response.code());
            }

            String responseBody = response.body().string();
            JsonObject jsonResponse = gson.fromJson(responseBody, JsonObject.class);
            
            return parseVulnerabilityResult(jsonResponse);
        }
    }

    public String fixVulnerability(@NotNull String code, @NotNull Vulnerability vulnerability, @NotNull String language) throws IOException {
        JsonObject requestBody = new JsonObject();
        requestBody.addProperty("code", code);
        requestBody.add("vulnerability", gson.toJsonTree(vulnerability));
        requestBody.addProperty("language", language);

        RequestBody body = RequestBody.create(
            requestBody.toString(),
            MediaType.parse("application/json")
        );

        Request request = new Request.Builder()
            .url(apiUrl + "/fix")
            .post(body)
            .build();

        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new IOException("Fix API call failed: " + response.code());
            }

            String responseBody = response.body().string();
            JsonObject jsonResponse = gson.fromJson(responseBody, JsonObject.class);
            
            return jsonResponse.get("fixed_code").getAsString();
        }
    }

    private VulnerabilityResult parseVulnerabilityResult(JsonObject json) {
        List<Vulnerability> vulnerabilities = new ArrayList<>();
        
        if (json.has("vulnerabilities") && json.get("vulnerabilities").isJsonArray()) {
            com.google.gson.JsonArray vulnArray = json.getAsJsonArray("vulnerabilities");
            for (int i = 0; i < vulnArray.size(); i++) {
                com.google.gson.JsonElement element = vulnArray.get(i);
                if (element.isJsonObject()) {
                    JsonObject vulnJson = element.getAsJsonObject();
                    Vulnerability vuln = new Vulnerability(
                        vulnJson.get("type").getAsString(),
                        vulnJson.get("severity").getAsString(),
                        vulnJson.get("line").getAsInt(),
                        vulnJson.has("message") ? vulnJson.get("message").getAsString() : "",
                        vulnJson.has("cwe") ? vulnJson.get("cwe").getAsString() : null
                    );
                    vulnerabilities.add(vuln);
                }
            }
        }
        
        return new VulnerabilityResult(vulnerabilities);
    }

    private String getLanguageFromPath(String filePath) {
        String lowerPath = filePath.toLowerCase();
        if (lowerPath.endsWith(".py")) return "python";
        if (lowerPath.endsWith(".java")) return "java";
        if (lowerPath.endsWith(".js")) return "javascript";
        if (lowerPath.endsWith(".ts")) return "typescript";
        if (lowerPath.endsWith(".cpp") || lowerPath.endsWith(".cc") || lowerPath.endsWith(".cxx")) return "cpp";
        if (lowerPath.endsWith(".c")) return "c";
        return "python"; // default
    }
}

