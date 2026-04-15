import mongoose from 'mongoose';

const UserSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Please provide a name'],
  },
  email: {
    type: String,
    required: [true, 'Please provide an email'],
    unique: true,
    lowercase: true,
  },
  password: {
    type: String,
    required: [true, 'Please provide a password'],
  },
  businessName: {
    type: String,
    required: [true, 'Please provide a business name'],
  },
  phone: {
    type: String,
  },
  backend_user_id: {
    type: String,
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
});

// Structural prevention safely avoiding hot reloading mapping overwrites intrinsically  
export default mongoose.models.User || mongoose.model('User', UserSchema);
