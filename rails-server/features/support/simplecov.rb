require 'simplecov'
SimpleCov.start 'rails' do
  # Customize SimpleCov configuration here if needed
  add_filter 'test/' # Exclude test files
  add_filter 'spec/' # Exclude spec files
  add_filter 'features/' # Exclude feature files
end
