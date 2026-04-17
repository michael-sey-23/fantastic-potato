package com.dictionary.dict_backend.controller;

import com.dictionary.dict_backend.model.Role;
import com.dictionary.dict_backend.model.User;
import com.dictionary.dict_backend.security.JwtUtils;
import com.dictionary.dict_backend.repository.UserRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/auth")
public class AuthController {
    private final AuthenticationManager authenticationManager;
    private final UserDetailsService userDetailsService;
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtils jwtUtils;

    public AuthController(AuthenticationManager authenticationManager, UserDetailsService userDetailsService,
                          JwtUtils jwtUtils, UserRepository userRepository, PasswordEncoder passwordEncoder) {
        this.authenticationManager = authenticationManager;
        this.userDetailsService = userDetailsService;
        this.jwtUtils = jwtUtils;
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody Map<String, String> loginData) {
        String username = loginData.get("username");
        String password = loginData.get("password");
        // 1. Authenticate the user (Spring checks the password for us!)
        authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(username, password));
        // 2. Load the user's details
        final UserDetails userDetails = userDetailsService.loadUserByUsername(username);
        // 3. Extract the first authority (e.g. USER or ADMIN)
        String role = userDetails.getAuthorities().iterator().next().getAuthority();

        // 4. Generate a JWT token with that role included!
        final String jwt = jwtUtils.generateToken(userDetails.getUsername(), role);

        // 5. Return it back to the Angular app!
        return ResponseEntity.ok(Map.of("token", jwt));
    }

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody Map<String, String> regData) {
        String username = regData.get("username");
        String password = regData.get("password");

        // 1. Check if user already exists
        if (userRepository.findByUsername(username).isPresent()) {
            return ResponseEntity.badRequest().body(Map.of("error", "Username already taken!"));
        }

        // 2. Create the new User (Default to ROLE_USER)
        User newUser = new User();
        newUser.setUsername(username);
        newUser.setPassword(passwordEncoder.encode(password));
        newUser.setRole(Role.USER);

        userRepository.save(newUser);
        return ResponseEntity.ok(Map.of("message", "User registered successfully!"));
    }
}
