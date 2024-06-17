Given(/Im at the home page/) do 
    visit(root_path) # provided by Capybara, used to navigate to a path 
end 

When(/I click on past chat/) do 
    click_link("chat-1")
end 

# Analyst user story (uid = 1)
Then(/I should see the chat history/) do 
    message_text_0 = find('#message-content-1 .mb-0').text
    message_text_1 = find('#message-content-2 .mb-0').text
    expect(message_text_0).to eq('Tell me examples on text placeholders')
    expect(message_text_1).to eq('Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.')
end 

# New user user story (uid=3)
Then(/I should see no past chats/) do 
    ul = find('#past-chats')
    expect(ul).to have_no_css('li')
end 

When(/User enters a URL in the address bar/) do 
    visit('/c/2')
end 

# Analyst user story (uid = 1)
Then(/I should see an alert stopping me/) do 
    alert = find('.alert.alert-danger', visible: true)
    expect(alert.text).to include('You are not authorized to access this chat.')
end 