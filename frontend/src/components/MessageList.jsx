import Message from './Message'
import LoadingIndicator from './LoadingIndicator'
import './MessageList.css'

function MessageList({ messages, loading }) {
  return (
    <div className="message-list">
      {messages.map((message) => (
        <Message key={message.id} message={message} />
      ))}
      {loading && <LoadingIndicator />}
    </div>
  )
}

export default MessageList

