export default function Footer() {
  return (
    <footer className="w-full border-t border-gray-200 mt-20">
      <div className="max-w-6xl mx-auto px-6 py-6 flex flex-col md:flex-row items-center justify-between text-sm text-gray-500">
        
        <p>© {new Date().getFullYear()} AI Agent. All rights reserved.</p>

        <div className="flex gap-6 mt-3 md:mt-0">
          <span className="hover:text-black cursor-pointer">Privacy</span>
          <span className="hover:text-black cursor-pointer">Terms</span>
          <span className="hover:text-black cursor-pointer">Support</span>
        </div>

      </div>
    </footer>
  )
}