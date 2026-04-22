package com.dictionary.dict_backend.service;

import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.Map;

@Service
public class ChatService {

    private final WebClient webClient;

    public ChatService(WebClient.Builder webClientBuilder, @org.springframework.beans.factory.annotation.Value("${PYTHON_SERVICE_URL:http://localhost:8000}") String pythonServiceUrl) {
        // The Python AI service can be swapped between local and containerized hosts via config.
        String baseUrl = (pythonServiceUrl != null) ? pythonServiceUrl : "http://localhost:8000";
        this.webClient = webClientBuilder.baseUrl(baseUrl).build();
    }

    public Mono<Map<String, Object>> getAcronymResponse(String query) {
        // The Java layer stays thin here: it forwards the prompt and unwraps the Python response.
        return this.webClient.post()
                .uri("/chat")
                .bodyValue(java.util.Objects.requireNonNull(java.util.Map.of("query", query)))
                .retrieve()
                .bodyToMono(new org.springframework.core.ParameterizedTypeReference<Map<String, Object>>() {
                });
    }

    public Mono<Map<String, Object>> addAcronym(Map<String, String> data) {
        java.util.Objects.requireNonNull(data, "data cannot be null");
        return this.webClient.post()
                .uri("/admin/add")
                .bodyValue((Object) data)
                .retrieve()
                .bodyToMono(new org.springframework.core.ParameterizedTypeReference<Map<String, Object>>() {
                });
    }

    public Mono<java.util.List<Map<String, Object>>> getSuggestions() {
        return this.webClient.get()
                .uri("/admin/suggestions")
                .retrieve()
                .bodyToMono(new org.springframework.core.ParameterizedTypeReference<java.util.List<Map<String, Object>>>() {
                });
    }

    public Mono<java.util.List<Map<String, Object>>> getAllAcronyms() {
        return this.webClient.get()
                .uri("/admin/all-acronyms")
                .retrieve()
                .bodyToMono(new org.springframework.core.ParameterizedTypeReference<java.util.List<Map<String, Object>>>() {
                });
    }

    public Mono<Map<String, Object>> deleteSuggestion(int index) {
        return this.webClient.delete()
                .uri("/admin/suggestions/" + index)
                .retrieve()
                .bodyToMono(new org.springframework.core.ParameterizedTypeReference<Map<String, Object>>() {
                });
    }

    public Mono<Map<String, Object>> deleteAcronym(String acronym) {
        return this.webClient.delete()
                .uri("/admin/delete/" + acronym)
                .retrieve()
                .bodyToMono(new org.springframework.core.ParameterizedTypeReference<Map<String, Object>>() {
                });
    }

    public Mono<Map<String, Object>> updateAcronym(Map<String, String> data) {
        java.util.Objects.requireNonNull(data, "data cannot be null");
        return this.webClient.put()
                .uri("/admin/update")
                .bodyValue((Object) data)
                .retrieve()
                .bodyToMono(new org.springframework.core.ParameterizedTypeReference<Map<String, Object>>() {
                });
    }
}
