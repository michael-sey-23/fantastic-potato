package com.dictionary.dict_backend.controller;

import com.dictionary.dict_backend.model.SearchHistory;
import com.dictionary.dict_backend.repository.SearchHistoryRepository;
import com.dictionary.dict_backend.service.ChatService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/acronyms")
public class AcronymController {

    private final ChatService chatService;
    private final SearchHistoryRepository historyRepository;

    public AcronymController(ChatService chatService, SearchHistoryRepository historyRepository) {
        this.chatService = chatService;
        this.historyRepository = historyRepository;
    }

    @GetMapping("/search")
    public List<Map<String, String>> search(@RequestParam String query) {
        try {
            Map<String, Object> result = chatService.getAcronymResponse(query).block();
            String responseFromPython = (result != null && result.containsKey("response"))
                    ? result.get("response").toString()
                    : "No response from AI.";

            // Save to Search History
            String username = SecurityContextHolder.getContext().getAuthentication().getName();
            historyRepository.save(new SearchHistory(query, responseFromPython, username));

            return List.of(Map.of("definition", responseFromPython));
        } catch (Exception e) {
            return List.of(Map.of("definition", "Error: The AI service is unavailable."));
        }
    }

    @GetMapping("/history")
    public List<SearchHistory> getHistory() {
        String username = SecurityContextHolder.getContext().getAuthentication().getName();
        return historyRepository.findByUsernameOrderBySearchTimeDesc(username);
    }

    @PostMapping("/add")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Map<String, Object>> addAcronym(@RequestBody Map<String, String> data) {
        try {
            Map<String, Object> result = chatService.addAcronym(data).block();
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", "Error updating AI dictionary: " + e.getMessage()));
        }
    }

    @GetMapping("/suggestions")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<List<Map<String, String>>> getSuggestions() {
        try {
            List<Map<String, String>> result = chatService.getSuggestions().block();
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(null);
        }
    }

    @DeleteMapping("/suggestions/{index}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Map<String, Object>> deleteSuggestion(@PathVariable int index) {
        try {
            Map<String, Object> result = chatService.deleteSuggestion(index).block();
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", "Error deleting suggestion: " + e.getMessage()));
        }
    }

    @GetMapping("/all-acronyms")
    public ResponseEntity<List<Map<String, String>>> getAcronyms() {
        try {
            List<Map<String, String>> result = chatService.getAllAcronyms().block();
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(null);
        }
    }

    @PutMapping("/update")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Map<String, Object>> updateAcronym(@RequestBody Map<String, String> data) {
        try {
            Map<String, Object> result = chatService.updateAcronym(data).block();
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", "Error updating AI dictionary: " + e.getMessage()));
        }
    }

    @DeleteMapping("/delete/{acronym}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Map<String, Object>> deleteAcronym(@PathVariable String acronym) {
        try {
            Map<String, Object> result = chatService.deleteAcronym(acronym).block();
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", "Error deleting acronym: " + e.getMessage()));
        }
    }

}
