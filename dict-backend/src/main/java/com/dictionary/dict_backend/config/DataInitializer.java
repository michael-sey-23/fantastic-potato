package com.dictionary.dict_backend.config;

import com.dictionary.dict_backend.model.Role;
import com.dictionary.dict_backend.model.User;
import com.dictionary.dict_backend.repository.UserRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

@Component
public class DataInitializer implements CommandLineRunner{

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public DataInitializer(UserRepository userRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Override
    public void run(String... args) {
        // Seed a default admin account for local development the first time the app starts.
        if (userRepository.findByUsername("admin").isEmpty()) {
            User admin = new User();
            admin.setUsername("admin");
            admin.setPassword(passwordEncoder.encode("password123"));
            admin.setRole(Role.ADMIN);
            userRepository.save(admin);
            System.out.println("✅ Data Initialization Complete: Created 'admin' user.");
        } else {
            System.out.println("ℹ️ Skipping initialization: 'admin' user already exists.");
        }
    }
}
