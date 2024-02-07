enum AppStatus {
    LoggingIn = "AUTHENTICATING",
    InitializingData = "LOADING DATA",
    GettingMessageHistory = "GETTING MESSAGE HISTORY",
    SavingConversation = "SAVING CONVERSATION",
    GeneratingChatResponse = "GENERATING CHAT RESPONSE",
    Idle = "IDLE",
    Error = "ERROR" // you can add as many statuses as needed
  }

  export default AppStatus;