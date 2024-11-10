import streamlit as st
import fitz
import base64
from tempfile import NamedTemporaryFile

from annotator import annotator

on = st.toggle("Are you teacher?")
is_summarized = False
if on:
    st.write("You're teacher now")
    is_summarized = st.button("Summarize questions")

st.subheader("Ask questions")

user_input = st.text_input("Enter document ID", 2)
process_button = st.button("Go!")

# When the button is clicked, process the input
#if process_button:
user_id = 2
doc_id = 2
supabase_url = 'https://lndnrkmllszfkltxmqqw.supabase.co'
supabase_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxuZG5ya21sbHN6ZmtsdHhtcXF3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzEwNjMzOTYsImV4cCI6MjA0NjYzOTM5Nn0.Z8PPI83b3uyhc19GskQgOMHVJmuS7DHZ3EexFE8LFzY'

args = {
    'user_id': user_id,
    'doc_id': doc_id,
    'supabase_url': supabase_url,
    'supabase_key': supabase_key
}

num_clicks = annotator(args)

if is_summarized:
    st.write("""
        Here are the students' questions summarized:

        **Questions:**

        * **Romania's position**: What does it mean for Romania to be "between East and West"? How did this affect their history? Why did Romanians have to choose between the East and West throughout their history?
        * **Socio-economic transition**: How did the transition from an agricultural society to an industrial economy happen, and why was it slow at first?
        * **Communist modernization**: What kind of "modernization" did the Communists pursue, and how was it different from earlier modernization efforts? Why is the interwar period described as a time when modernization accelerated?
        * **Feudalism**: What does "feudalism, of a sort" mean? How was Romanian feudalism different from other European countries?

        **Problems:**

        * The students seemed unclear on how Romania's position between East and West has impacted its history and culture. Some questions asked this topic multiple times, indicating a need for further clarification.
        * There were difficulties in understanding the specifics of the socio-economic transition in Romania, particularly regarding the pace of industrialization and urbanization.
        * The Communist modernization efforts posed some challenges for the students, with many questions seeking to understand how this was distinct from earlier periods of modernization.
    """)