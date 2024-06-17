# Tests for first sprint

Feature: For different users, display list of chats and chat history for each chat 
    As a Analyst, I want to access my past 20 chats
        so that I can access any of them from the home page.
    As a New User, I want to see that I have no chats
        so that I know that I have a brand new account

    Background: 
        Given Im at the home page 

    # Scenario: analyst account (uid=1)
    #     When I click on past chat 
    #     Then I should see the chat history 

    Scenario: new user account 
        Then I should see no past chats 