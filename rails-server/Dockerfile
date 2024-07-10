# Use the official lightweight Ruby image.
# https://hub.docker.com/_/ruby
FROM ruby:3.3.1 AS rails-toolbox    

# Install Node.js, Yarn, dos2unix, and dependencies
RUN curl -sS https://deb.nodesource.com/gpgkey/nodesource.gpg.key | gpg --dearmor | apt-key add - && \
    echo "deb https://deb.nodesource.com/node_14.x buster main" > /etc/apt/sources.list.d/nodesource.list && \
    curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && \
    echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list && \
    apt-get update && apt-get install -y nodejs yarn lsb-release libpq-dev python3-distutils dos2unix

# Set working directory
WORKDIR /app

# Copy Gemfile and Gemfile.lock
COPY Gemfile Gemfile.lock ./

# Install gems
RUN gem install bundler && \
    bundle config set --local deployment 'true' && \
    bundle config set --local without 'development test' && \
    bundle install

# Copy application code
COPY . /app

# Ensure /app/bin/rails and other scripts have execute permissions
RUN chmod -R +x /app/bin/*

# Convert line endings from DOS to Unix
RUN find /app/bin -type f -exec dos2unix {} \;

# Ensure correct ownership of the application directory
RUN chown -R root:root /app

# Set environment variables
ENV RAILS_ENV=production
ENV RAILS_SERVE_STATIC_FILES=true
ENV RAILS_LOG_TO_STDOUT=true
ENV SECRET_KEY_BASE='cfecc4c9cd963cbe9dad280e985daa3e'

# Expose port 8080
EXPOSE 8080

# Start Rails server
CMD ["bin/rails", "server", "-b", "0.0.0.0", "-p", "8080"]
