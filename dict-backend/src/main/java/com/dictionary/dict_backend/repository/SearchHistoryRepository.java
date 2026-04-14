package com.dictionary.dict_backend.repository;

import com.dictionary.dict_backend.model.SearchHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface SearchHistoryRepository extends JpaRepository<SearchHistory, Long> {
    List<SearchHistory> findByUsernameOrderBySearchTimeDesc(String username);
}
