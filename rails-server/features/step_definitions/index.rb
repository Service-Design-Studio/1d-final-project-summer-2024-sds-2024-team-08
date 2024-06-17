Given(/Im at the home page/) do 
    visit(root_path) # provided by Capybara, used to navigate to a path 
end 

When(/I click on past chat/) do 
    click_link("chat-1")
end 

# Analyst user story 
Then(/I should see the chat history/) do 
    # check correct url first 
    # check contents of chat history 
end 

# New user user story (uid=3)
Then(/I should see no past chats/) do 
    ul = find('#past-chats')
    expect(ul).to have_no_css('li')
end 