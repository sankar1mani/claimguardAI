# Frontend Application 🎨

> **React + Vite frontend for ClaimGuard AI - User interface for claim submission**

**🌐 Live Demo**: [Visit ClaimGuard AI](https://your-vercel-url.vercel.app) _(Replace with your actual Vercel URL)_

---

## 📋 Overview

Modern, responsive web application for submitting and tracking insurance claims.

**Tech Stack**: React 18, Vite, Tailwind CSS, React Router

**Deployment**: Hosted on Vercel for instant access

---

## 🚀 Quick Start

### With Docker (Recommended)

```bash
cd docker
docker compose up frontend
```

App will be available at: **http://localhost:5173**

### Without Docker

```bash
cd frontend
npm install
npm run dev
```

---

## ✨ Features

- 📤 **File Upload**: Drag-and-drop receipt upload
- 🔍 **Real-time Processing**: Watch claim processing in real-time
- 📊 **Detailed Results**: View itemized breakdown of approved/rejected items
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile
- 🎨 **Modern UI**: Clean, professional interface with Tailwind CSS

---

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── FileUpload.jsx
│   │   ├── ClaimForm.jsx
│   │   └── ResultsDisplay.jsx
│   ├── pages/             # Page components
│   │   ├── Home.jsx
│   │   └── Results.jsx
│   ├── App.jsx            # Main app component
│   └── main.jsx           # Entry point
├── public/                # Static assets
├── index.html            # HTML template
├── package.json          # Dependencies
├── vite.config.js        # Vite configuration
└── tailwind.config.js    # Tailwind CSS config
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `frontend/` directory:

```env
VITE_API_URL=http://localhost:8000
VITE_KESTRA_URL=http://localhost:8080
```

### API Integration

The frontend communicates with the backend API:

```javascript
// Example API call
const response = await fetch(`${import.meta.env.VITE_API_URL}/api/analyze`, {
  method: 'POST',
  body: formData
});
```

---

## 🎨 Styling

### Tailwind CSS

The app uses Tailwind CSS for styling. Key configuration:

```javascript
// tailwind.config.js
module.exports = {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        secondary: '#10B981'
      }
    }
  }
}
```

### Custom Components

Reusable components are styled with Tailwind classes:

```jsx
<button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg">
  Submit Claim
</button>
```

---

## 📦 Dependencies

Key packages:
- `react` - UI library
- `react-router-dom` - Routing
- `vite` - Build tool
- `tailwindcss` - CSS framework
- `axios` - HTTP client

Install all:
```bash
npm install
```

---

## 🛠️ Development

### Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

### Adding New Pages

1. Create component in `src/pages/`
2. Add route in `src/App.jsx`:

```jsx
<Route path="/new-page" element={<NewPage />} />
```

### Adding New Components

1. Create component in `src/components/`
2. Import and use in pages:

```jsx
import MyComponent from '../components/MyComponent';
```

---

## 🧪 Testing

### Manual Testing

1. Start the dev server: `npm run dev`
2. Open http://localhost:5173
3. Test file upload with sample receipts from `data/` folder
4. Verify results display correctly

### Build Testing

```bash
npm run build
npm run preview
```

---

## 🚀 Deployment

### Vercel (Recommended)

The app is configured for Vercel deployment:

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

Configuration is in `vercel.json`.

### Other Platforms

Build the app:
```bash
npm run build
```

Deploy the `dist/` folder to any static hosting service:
- Netlify
- GitHub Pages
- AWS S3
- Cloudflare Pages

---

## 🐛 Troubleshooting

### Port Already in Use

```
Error: Port 5173 is already in use
```
**Solution**: Change port in `vite.config.js` or kill the process using port 5173

### API Connection Errors

```
Error: Failed to fetch
```
**Solution**: 
1. Check backend is running at http://localhost:8000
2. Verify `VITE_API_URL` in `.env`
3. Check browser console for CORS errors

### Build Errors

```
Error: Cannot find module
```
**Solution**: Delete `node_modules` and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

---

## 📚 Learn More

- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [Main Project README](../README.md)

---

**Built with ❤️ for Assemble Hack 2025**
