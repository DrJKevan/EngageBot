Integrating the chatbot application with the LTI Launch Server involves handling session information retrieved via an API call to the Flask app. This setup enables the chatbot to provide a personalized experience based on the user's role and other context information obtained during the LTI launch process.

#### API Call to Flask from Streamlit

To facilitate the integration, the Flask app exposes an API endpoint (`/display_role`) that the Streamlit app can call to retrieve session information, such as the user's role. Below is an example of how you might implement this in your Streamlit app:

```python
import requests

# Example of making an API call to the Flask app to get session information
response = requests.get('http://localhost:5000/display_role')
if response.status_code == 200:
    user_info = response.json()
    user_role = user_info.get('role', 'Unknown')
    # Use the user_role or other session information in the Streamlit app
```

#### Explanation of the Code

- **Making an API Request:** The `requests` library is used to perform a GET request to the Flask app's `/display_role` endpoint, which returns the stored user information, including their role.
- **Handling the Response:** The response is checked for a successful status code (200). If successful, the JSON payload is parsed to extract the user's role.
- **Using Session Information:** The retrieved role (or other relevant session information) can then be used within the Streamlit app to customize the user experience, such as tailoring the chatbot's responses or available functionalities based on whether the user is a student, instructor, etc.

#### Testing the Chatbot

- **Local Testing:** While developing, you can test the integration locally by running both the Flask and Streamlit apps on your machine. Ensure the Flask app is accessible at the URL specified in the Streamlit app's API call (e.g., `http://localhost:5000/display_role`).
- **Simulate LTI Launches:** Use tools like Postman or the IMS Global LTI 1.3 Reference Implementation tool to simulate LTI launches to your Flask app and ensure that the correct session information is being stored and can be retrieved by the Streamlit app.
- **Role-Based Customization:** Implement logic in your Streamlit app to respond differently based on the user's role. For example, you might present different sets of questions to students and instructors or customize the interface accordingly.

#### Ensuring Security

When expanding functionality, especially with API calls between services, it's crucial to ensure secure communication. Consider implementing authentication for the API endpoint, such as requiring a token that the Streamlit app must provide to access the session information. Additionally, validate the data received from the Flask app to prevent injection attacks or other security vulnerabilities.