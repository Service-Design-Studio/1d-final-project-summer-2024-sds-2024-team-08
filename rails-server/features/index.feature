# Tests for first sprint

Feature: For different users, display list of chats and chat history for each chat 
    As a Analyst, I want to access my past 20 chats
        so that I can access any of them from the home page.
    As a New User, I want to see that I have no chats
        so that I know that I have a brand new account

    Background: 
        Given Im at the home page 

    Scenario: analyst account (uid=2)
        When I click on past chat 
        Then I should see the chat history 

    Scenario: new user account (uid=3)
        When I switch to a new account
        Then I should see no past chats

    Scenario: any user account (uid=3)
        When I attempt to access a chat by url that is not mine
        Then I should see an alert stopping me