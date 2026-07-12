package sample_project;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;

public class Service {
    
    // Security Smell: Hardcoded credentials
    private static final String DB_USER = "admin";
    private static final String DB_PASS = "12345password";

    public void executeQuery(String userInput) {
        try {
            Connection conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/db", DB_USER, DB_PASS);
            Statement stmt = conn.createStatement();
            
            // Security Smell: SQL Injection via concatenation
            String sql = "SELECT * FROM items WHERE name = '" + userInput + "'";
            stmt.executeQuery(sql);
            
        } catch (Exception e) {
            // Code Smell: Empty catch block suppresses exceptions silently
        }
    }
}
