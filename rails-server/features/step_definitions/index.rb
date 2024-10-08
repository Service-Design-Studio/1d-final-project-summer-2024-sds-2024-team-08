Given(/Im at the home page/) do
    visit(root_path) # provided by Capybara, used to navigate to a path
end

# Analyst user story (uid = 1)
When(/I click on past chat/) do
    click_link("chat-2")
end

# Analyst user story (uid = 1)
Then(/I should see the chat history/) do
    expected_messages = [
    'Tell me examples on text placeholders',
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
  ]

  expected_messages.each do |expected_message|
    expect(page).to have_content(expected_message)
  end
end

# New user user story (uid=1)
When(/I switch to a new account/) do
    find("[data-test='change-user-dropdown']").click
    find("[data-test='user-1-link']").click
end

# New user user story (uid=1)
Then(/I should see no past chats/) do
    ul = find('#past-chats')
    expect(ul).to have_no_css('li')
end

# Any user story (uid = 3)
When(/I attempt to access a chat by url that is not mine/) do
    visit('/c/2')
end

# Any user story (uid = 3)
Then(/I should see an alert stopping me/) do
    alert = find('.alert.alert-danger', visible: true)
    expect(alert.text).to include('You are not authorized to access this chat.')
end

# Any user story (uid = 3)
When(/I ask Genie who is Ben Carson/) do
    find("[data-test='change-user-dropdown']").click
    find("[data-test='user-3-link']").click
    click_link("chat-8")
    fill_in 'message', with: 'Who is Ben Carson?'
    find('button[name="button"]').click
end

Then(/I should see the question asked disappear/) do
    expect(page).not_to have_selector('#message', text: 'Who is Ben Carson?')
end

Then(/I should see the response containing Ben Carson's information/) do
    sleep(5)
    expect(page).to have_content(/.*Ben Carson.*is.*/)
end

#Incorrect spelling
When(/I ask Genie Who is donal dtrump/) do
    click_link("chat-8")
    fill_in 'message', with: 'Who is donal dtrump?'
    find('button[name="button"]').click
end

Then(/I should see the response asking which names and it includes Donald Trump/) do
    sleep(5)
    expect(page).to have_content(/Which names.*donald trump.*/i)
end

#Lowercase nospace
When(/I ask Genie Tell me more about joebiden/) do
    click_link("chat-8")
    fill_in 'message', with: 'Tell me more about joebiden'
    find('button[name="button"]').click
end

Then(/I should see the response asking which names and it includes Joe Biden/) do
    sleep(5)
    expect(page).to have_content(/Which names.*joe biden.*/i)
end

#Lowercase nospace
When(/I ask Genie Tell me more about oka kurniawan/) do
    click_link("chat-8")
    fill_in 'message', with: 'Tell me more about oka kurniawan'
    find('button[name="button"]').click
end

Then(/I should see the response saying it cannot find any information/) do
    sleep(5)
    expect(page).to have_content(/I.*any information.*/i)
end

# network graph stuff 
sacrificial_chat = "chat-8"
When(/^I ask for a network graph about stakeholders$/) do 
    click_link(sacrificial_chat)
    fill_in 'message', with: 'show me a graph of ben carson relationships'
    find('button[name="button"]').click
end

Then(/I should see a network graph/) do 
    sleep(20)

    chat_history = find('#chat-history-child')

    # initial_div_count = chat_history.all('div').size
    last_div = chat_history.all('div').last
    
    # Timeout.timeout(30) do
    #     loop do
    #         divs = chat_history.all('div')
    #         if divs.size > initial_div_count
    #             last_div = divs.last
    #             break
    #         end
    #         sleep 0.1
    #     end
    # end

    puts "aaaa"

    expect(last_div).not_to be_nil
    expect(last_div).to have_css('iframe')
end

When(/^I ask for a network graph about stakeholders but there is not enough information$/) do 
    click_link(sacrificial_chat)
    fill_in 'message', with: 'show me a graph of loheesong relationships'
    find('button[name="button"]').click
end

Then(/I should see the response saying insufficient information for graph/) do 
    sleep(5)

    chat_history = find('#chat-history')
    last_div = chat_history.all('div').last

    expect(last_div).not_to be_nil
    expect(last_div).not_to have_selector('p')
end

When(/^I ask for a relationship between stakeholders that involves media content$/) do 
  click_link(sacrificial_chat)
  fill_in 'message', with: 'Generate a network graph of the relationship between ExxonMobil and Ivanka Trump.'
  find('button[name="button"]').click
end

When(/I send a GET request/) do 
    page.execute_script('
        fetch("https://python-server-ohgaalojiq-de.a.run.app/", {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
        }).then(response => response.json()).then(data => {
            document.body.innerHTML += `<div id="response">${data.message}</div>`;
        }).catch(error => {
            document.body.innerHTML += `<div id="error">${error.message}</div>`;
        });
    ')
    expect(page).to have_selector('#response, #error', wait: 10)
end
