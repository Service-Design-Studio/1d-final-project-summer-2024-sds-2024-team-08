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

    Scenario: new user account (uid=1)
        When I switch to a new account
        Then I should see no past chats

    Scenario: any user account (uid=1)
        When I attempt to access a chat by url that is not mine
        Then I should see an alert stopping me

    Scenario: asking Genie question (correct spelling) (uid=3)
        When I ask Genie who is Ben Carson
        Then I should see the question asked disappear
        And I should see the response containing Ben Carson's information

    Scenario: asking Genie question (incorrect spelling) (uid=3)
        When I ask Genie Who is donal dtrump
        Then I should see the response asking which names and it includes Donald Trump

    Scenario: asking Genie question (lowercase no space) (uid=3)
        When I ask Genie Tell me more about joebiden
        Then I should see the response asking which names and it includes Joe Biden

    Scenario: SAD PATH: asking Genie question (uid=3)
        When I ask Genie Tell me more about oka kurniawan
        Then I should see the response saying it cannot find any information

    Scenario: explicitly asking for graph (uid=3) 
        When I ask for a network graph about stakeholders 
        Then I should see a network graph 

    Scenario: SAD PATH: explicitly asking for graph (uid=3) 
        When I ask for a network graph about stakeholders but there is not enough information 
        Then I should see the response saying insufficient information for graph 

    # sprint 4 
    Scenario: Draw insights from media for network graph (uid=3) 
        When I ask for media content
        Then I should see a response with media content
        Then I ask for a network graph based on the media content 
        Then I should see a network graph 

    Scenario: SAD PATH: Draw insights from media for network graph (uid=3) 
        When I ask for media content but there isnt enough information
        Then I should see the response saying insufficient information