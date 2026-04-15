import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import bcrypt from "bcryptjs";
import { connectDB } from "@/lib/mongodb";
import User from "@/models/User";

const handler = NextAuth({
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          throw new Error("Invalid credentials payload logically structurally absent");
        }

        await connectDB();
        
        // Find specific target natively implicitly bound sequentially
        const user = await User.findOne({ email: credentials.email });
        if (!user) {
          throw new Error("No existing credentials mapped natively explicitly");
        }

        // Validate strictly encrypted bounds cleanly isolating hash layers sequentially natively
        const isValid = await bcrypt.compare(credentials.password, user.password);
        if (!isValid) {
          throw new Error("Invalid credentials explicit mismatch naturally");
        }

        return {
          id: user._id.toString(),
          name: user.name,
          email: user.email,
          businessName: user.businessName,
          backend_user_id: user.backend_user_id
        };
      }
    })
  ],
  session: {
    strategy: "jwt",
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        // Encrypt explicitly loaded variables mapping user structures into explicit token arrays natively 
        token.id = user.id;
        token.businessName = user.businessName;
        token.backend_user_id = user.backend_user_id;
      }
      return token;
    },
    async session({ session, token }) {
      if (token) {
        // Expose tokens safely into client session structs securely explicitly natively
        session.user.id = token.id;
        session.user.businessName = token.businessName;
        session.user.backend_user_id = token.backend_user_id;
      }
      return session;
    }
  },
  pages: {
    signIn: "/login",
  },
  secret: process.env.NEXTAUTH_SECRET,
});

export { handler as GET, handler as POST };
