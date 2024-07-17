# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[7.1].define(version: 0) do
  # These are extensions that must be enabled in order to support this database
  enable_extension "plpgsql"

  create_table "chats", primary_key: "chat_id", id: :serial, force: :cascade do |t|
    t.integer "user_id", null: false
  end

  create_table "messages", primary_key: "message_id", id: :serial, force: :cascade do |t|
    t.integer "chat_id", null: false
    t.integer "sender_id", null: false
    t.text "role", null: false
    t.text "content", null: false
    t.check_constraint "role = ANY (ARRAY['user'::text, 'assistant'::text])", name: "messages_role_check"
  end

  create_table "users", primary_key: "user_id", id: :serial, force: :cascade do |t|
    t.text "name", null: false
  end

  add_foreign_key "chats", "users", primary_key: "user_id", name: "chats_user_id_fkey", on_delete: :cascade
  add_foreign_key "messages", "chats", primary_key: "chat_id", name: "messages_chat_id_fkey", on_delete: :cascade
  add_foreign_key "messages", "users", column: "sender_id", primary_key: "user_id", name: "messages_sender_id_fkey", on_delete: :cascade
end
