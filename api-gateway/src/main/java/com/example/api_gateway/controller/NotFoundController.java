package com.example.api_gateway.controller;

import java.util.Map;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class NotFoundController {

    @RequestMapping("/not-found")
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public Map<String, Object> notFound() {
        return Map.of(
            "status", 404,
            "error", "No encontrado",
            "mensaje", "La Api no tiene esta ruta"
        );
        
    }
}
