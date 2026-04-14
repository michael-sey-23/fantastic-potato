package com.dictionary.dict_backend.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "search_history")
public class SearchHistory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String query;
    private String response;
    
    @Column(name = "search_time")
    private LocalDateTime searchTime;

    private String username;

    public SearchHistory() {}

    public SearchHistory(String query, String response, String username) {
        this.query = query;
        this.response = response;
        this.username = username;
        this.searchTime = LocalDateTime.now();
    }

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getQuery() { return query; }
    public void setQuery(String query) { this.query = query; }
    public String getResponse() { return response; }
    public void setResponse(String response) { this.response = response; }
    public LocalDateTime getSearchTime() { return searchTime; }
    public void setSearchTime(LocalDateTime searchTime) { this.searchTime = searchTime; }
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
}
