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
@RequestMapping("/api/")
public class AcronymController {

    private final ChatService chatService;
    private final SearchHistoryRepository historyRepository;

    public AcronymController(ChatService chatService, SearchHistoryRepository historyRepository) {
        this.chatService = chatService;
        this.historyRepository = historyRepository;
    }

    @GetMapping("acronyms/search")
    public List<Map<String, String>> search(@RequestParam String query) {
        try {
            // Spring delegates the actual acronym lookup to the Python AI service.
            Map<String, Object> result = chatService.getAcronymResponse(query).block();
            String responseFromPython = (result != null && result.containsKey("response"))
                    ? result.get("response").toString()
                    : "No response from AI.";

            // Search history is stored per authenticated user so the history page can
            // show previous lookups after login.
            String username = SecurityContextHolder.getContext().getAuthentication().getName();
            historyRepository.save(new SearchHistory(query, responseFromPython, username));

            return List.of(Map.of("definition", responseFromPython));
        } catch (Exception e) {
            return List.of(Map.of("definition", "Error: The AI service is unavailable."));
        }
    }

    @GetMapping("acronyms/history")
    public List<SearchHistory> getHistory() {
        // Users only see their own history records, not global search traffic.
        String username = SecurityContextHolder.getContext().getAuthentication().getName();
        return historyRepository.findByUsernameOrderBySearchTimeDesc(username);
    }

    @PostMapping("acronyms/add")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Map<String, Object>> addAcronym(@RequestBody Map<String, String> data) {
        try {
            Map<String, Object> result = chatService.addAcronym(data).block();
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", "Error updating AI dictionary: " + e.getMessage()));
        }
    }

    @GetMapping("acronyms/suggestions")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<List<Map<String, Object>>> getSuggestions() {
        try {
            List<Map<String, Object>> result = chatService.getSuggestions().block();
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            // Log detail to aid debugging when the Python AI service is unreachable or errors.
            e.printStackTrace();
            // Return a clear, non-200 status with a simple error payload the frontend can inspect.
            return ResponseEntity.status(503).body(List.of(Map.of("error", "AI service unavailable")));
        }
    }

    @DeleteMapping("acronyms/suggestions/{index}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Map<String, Object>> deleteSuggestion(@PathVariable int index) {
        try {
            Map<String, Object> result = chatService.deleteSuggestion(index).block();
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", "Error deleting suggestion: " + e.getMessage()));
        }
    }

    @GetMapping("acronyms/all-acronyms")
    public ResponseEntity<List<Map<String, Object>>> getAcronyms() {
        try {
            List<Map<String, Object>> result = chatService.getAllAcronyms().block();
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(503).body(List.of(Map.of("error", "AI service unavailable")));
        }
    }

    @PutMapping("acronyms/update")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Map<String, Object>> updateAcronym(@RequestBody Map<String, String> data) {
        try {
            Map<String, Object> result = chatService.updateAcronym(data).block();
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("error", "Error updating AI dictionary: " + e.getMessage()));
        }
    }

    @DeleteMapping("acronyms/delete/{acronym}")
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
