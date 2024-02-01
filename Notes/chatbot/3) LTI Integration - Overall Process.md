A working LTI setup comprises several components, each playing a crucial role in ensuring secure and seamless integration between the external tool (e.g., a chatbot) and the LMS (e.g., Brightspace D2L). The key components and their functionalities are as follows:

- **LTI Launch Server (Flask App):** A backend server that handles LTI 1.3 launch requests from the LMS. It authenticates these requests using OAuth 2.0 and JWT, validates them, and then redirects users to the appropriate external tool, such as a Streamlit chatbot app, with the necessary context and permissions.
    
- **Chatbot Application (Streamlit App):** A frontend application where the actual interaction with users takes place. It receives context from the LTI Launch Server, such as user information and course details, to provide a personalized experience.
    
- **LTI Configuration in the LMS:** This involves setting up the external tool within the LMS using specific URLs for launch, redirection, and keyset, along with other necessary configuration details like client ID and secret.
    
- **Information Exchange:** During the launch process, information such as user identity, roles, and course details are securely passed from the LMS to the external tool via the LTI Launch Server. This is facilitated by JWTs, which carry this information in a secure and standardized format.
    
- **Process Flow:**
    
    1. **LMS Configuration:** The external tool is configured in the LMS with necessary URLs and credentials.
    2. **LTI Launch Request:** Initiated by the user accessing the tool within the LMS, sending a launch request to the LTI Launch Server.
    3. **Authentication and Validation:** The LTI Launch Server authenticates the request, validates the JWT, and extracts the necessary information.
    4. **Redirection:** Users are redirected to the external tool (e.g., Streamlit app) with the appropriate context for a personalized experience.

Files and their roles:

- **Flask App File (`lti_app.py`):** Manages LTI launch requests, including authentication and redirection.
- **Streamlit App File:** Provides the user interface for the chatbot, utilizing information passed from the Flask app to interact with users within their course context.