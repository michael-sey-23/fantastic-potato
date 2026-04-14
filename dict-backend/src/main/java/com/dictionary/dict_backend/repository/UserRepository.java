package com.dictionary.dict_backend.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import com.dictionary.dict_backend.model.User;

import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {

    public Optional<User> findByUsername(String username);
}
