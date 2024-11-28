import streamlit as st
import sqlite3
from datetime import date
import random

# Database functions
def create_database():
    conn = sqlite3.connect("train_tickets.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            train TEXT,
            travel_date TEXT,
            seat TEXT,
            UNIQUE(train, travel_date, seat)  -- Ensure unique seats per train and date
        )
    """)
    conn.commit()
    conn.close()


def book_ticket_db(name, train, travel_date, seat):
    conn = sqlite3.connect("train_tickets.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tickets (name, train, travel_date, seat)
        VALUES (?, ?, ?, ?)
    """, (name, train, travel_date, seat))
    conn.commit()
    ticket_id = cursor.lastrowid
    conn.close()
    return ticket_id


def get_all_tickets():
    conn = sqlite3.connect("train_tickets.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets")
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_ticket(ticket_id):
    conn = sqlite3.connect("train_tickets.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tickets WHERE ticket_id = ?", (ticket_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0


def get_booked_seats(train, travel_date):
    conn = sqlite3.connect("train_tickets.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT seat FROM tickets WHERE train = ? AND travel_date = ?
    """, (train, travel_date))
    booked_seats = {row[0] for row in cursor.fetchall()}
    conn.close()
    return booked_seats


def allocate_seat(all_seats, booked_seats):
    available_seats = [seat for seat in all_seats if seat not in booked_seats]
    return random.choice(available_seats) if available_seats else None


# Streamlit app
def main():
    st.title("Train Ticket Management System")

    create_database()  # Ensure database and table exist

    # Predefined list of seats in the bogie
    all_seats = [f"{row}{col}" for row in range(1, 11) for col in "ABC"]

    st.subheader("Choose an Action")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Book Ticket"):
            st.session_state["action"] = "book"

    with col2:
        if st.button("View Tickets"):
            st.session_state["action"] = "view"

    with col3:
        if st.button("Cancel Ticket"):
            st.session_state["action"] = "cancel"

    # Handle actions
    if "action" in st.session_state:
        if st.session_state["action"] == "book":
            st.subheader("Book a Train Ticket")
            name = st.text_input("Passenger Name")
            train = st.text_input("Train Name/Number")
            travel_date = st.date_input("Travel Date", value=date.today())

            if st.button("Confirm Booking"):
                if name and train:
                    booked_seats = get_booked_seats(train, str(travel_date))
                    seat = allocate_seat(all_seats, booked_seats)
                    if seat:
                        try:
                            ticket_id = book_ticket_db(name, train, str(travel_date), seat)
                            st.success(f"Ticket booked successfully! Ticket ID: {ticket_id}, Seat: {seat}")
                        except sqlite3.IntegrityError:
                            st.error("Seat already booked. Try again!")
                    else:
                        st.error("No seats available for the selected train and date.")
                else:
                    st.error("Please fill in all the details to book a ticket.")

        elif st.session_state["action"] == "view":
            st.subheader("View Booked Tickets")
            tickets = get_all_tickets()

            if tickets:
                for ticket in tickets:
                    st.write(f"**Ticket ID:** {ticket[0]}")
                    st.write(f"- Name: {ticket[1]}")
                    st.write(f"- Train: {ticket[2]}")
                    st.write(f"- Date: {ticket[3]}")
                    st.write(f"- Seat: {ticket[4]}")
                    st.write("---")
            else:
                st.info("No tickets have been booked yet.")

        elif st.session_state["action"] == "cancel":
            st.subheader("Cancel a Ticket")
            ticket_id = st.number_input("Enter Ticket ID to Cancel", min_value=1, step=1)

            if st.button("Confirm Cancellation"):
                if delete_ticket(ticket_id):
                    st.success("Ticket canceled successfully!")
                else:
                    st.error("Invalid Ticket ID. Please try again.")


if __name__ == "__main__":
    main()
