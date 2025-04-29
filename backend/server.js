const express = require('express');
const socketio = require('socket.io');
const crypto = require('crypto');
const app = express();
const PORT = process.env.PORT || 3000;

// Serve static files
app.use(express.static('public'));

// In-memory "database" (for demo only)
const users = {};
const rooms = {
  'general': { users: {}, messages: [] },
  'random': { users: {}, messages: [] }
};

// Generate a simple E2EE key pair for demo purposes
function generateKeys() {
  const { publicKey, privateKey } = crypto.generateKeyPairSync('rsa', {
    modulusLength: 2048,
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
  });
  return { publicKey, privateKey };
}

const server = app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

const io = socketio(server);

io.on('connection', (socket) => {
  console.log('New user connected');

  // Quick login
  socket.on('quickLogin', (username) => {
    if (!username) return;
    
    // Generate keys for the user
    const { publicKey, privateKey } = generateKeys();
    
    users[socket.id] = {
      id: socket.id,
      username,
      publicKey,
      privateKey
    };
    
    socket.emit('loggedIn', {
      username,
      privateKey, // In real app, this should be handled more securely
      rooms: Object.keys(rooms)
    });
  });

  // Join room
  socket.on('joinRoom', (roomName) => {
    if (!rooms[roomName]) {
      rooms[roomName] = { users: {}, messages: [] };
    }
    
    const user = users[socket.id];
    if (!user) return;
    
    rooms[roomName].users[socket.id] = user;
    socket.join(roomName);
    
    // Send room history and user list
    socket.emit('roomInfo', {
      name: roomName,
      messages: rooms[roomName].messages,
      users: Object.values(rooms[roomName].users).map(u => ({
        username: u.username,
        publicKey: u.publicKey
      }))
    });
    
    // Notify others
    socket.to(roomName).emit('userJoined', {
      username: user.username,
      publicKey: user.publicKey
    });
  });

  // Encrypted message
  socket.on('encryptedMessage', ({ room, encryptedMessage, iv, to }) => {
    const user = users[socket.id];
    if (!user || !rooms[room]) return;
    
    // In a real app, you'd verify the message signature here
    
    // Store message (encrypted)
    rooms[room].messages.push({
      from: user.username,
      fromPublicKey: user.publicKey,
      to,
      encryptedMessage,
      iv,
      timestamp: new Date().toISOString()
    });
    
    // Forward to recipient or broadcast to room
    if (to) {
      const recipient = Object.values(rooms[room].users).find(u => u.publicKey === to);
      if (recipient) {
        io.to(recipient.id).emit('newEncryptedMessage', {
          from: user.username,
          fromPublicKey: user.publicKey,
          encryptedMessage,
          iv
        });
      }
    } else {
      socket.to(room).emit('newEncryptedMessage', {
        from: user.username,
        fromPublicKey: user.publicKey,
        encryptedMessage,
        iv
      });
    }
  });

  // Disconnect
  socket.on('disconnect', () => {
    const user = users[socket.id];
    if (!user) return;
    
    // Remove user from all rooms
    Object.keys(rooms).forEach(roomName => {
      if (rooms[roomName].users[socket.id]) {
        delete rooms[roomName].users[socket.id];
        io.to(roomName).emit('userLeft', user.username);
      }
    });
    
    delete users[socket.id];
  });
});
