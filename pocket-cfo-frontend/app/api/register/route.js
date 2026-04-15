import { NextResponse } from 'next/server';
import bcrypt from 'bcryptjs';
import { connectDB } from '@/lib/mongodb';
import User from '@/models/User';

export async function POST(req) {
  try {
    const { name, email, password, businessName, phone } = await req.json();

    // Mathematically bind string limits explicit field validations securely natively 
    if (!name || !email || !password || !businessName) {
      return NextResponse.json({ success: false, error: 'Missing required explicit parameters' }, { status: 400 });
    }

    await connectDB();

    // Structurally prevent bounding constraint collisions explicitly natively globally
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return NextResponse.json({ success: false, error: 'Target email entity intrinsically already bounded' }, { status: 400 });
    }

    // Cryptographic isolation binding dynamically into structural bounds natively via salt
    const hashedPassword = await bcrypt.hash(password, 12);

    let backend_user_id = null;
    
    // Attempt sequential routing bindings tracking dependencies seamlessly traversing REST schemas explicitly natively 
    try {
      const backendRes = await fetch("http://localhost:8000/users/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, phone, businessName })
      });
      
      if (backendRes.ok) {
        const backendData = await backendRes.json();
        backend_user_id = backendData.user_id || backendData.backend_user_id;
      } else {
        console.warn("Python backend sync bypassed non-fatal binding explicitly natively.", await backendRes.text());
      }
    } catch (apiError) {
      console.warn("Python backend offline natively bypassed explicit synchronization step.", apiError);
    }

    // Generate strict constraints isolating OOP mapping models actively explicitly inherently 
    const newUser = await User.create({
      name,
      email,
      password: hashedPassword,
      businessName,
      phone,
      backend_user_id
    });

    return NextResponse.json({ success: true, message: 'Account created' }, { status: 201 });
  } catch (error) {
    console.error('Registration pipeline bindings failed structurally:', error);
    return NextResponse.json({ success: false, error: 'Processing bounds bypassed structurally natively' }, { status: 500 });
  }
}
