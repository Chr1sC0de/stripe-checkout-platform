import Image from "next/image";
import LoginButton from './loginButton';

export default function Home() {
  return (
    <main className="flex h-screen items-center justify-center p-4 md:p-24">
      <div className="flex flex-col items-center justify-center h-3/5 w-2/5">
        <div className="flex items-center justify-center h-full ">
          <Image
            src="/company-logo.png"
            alt="Company Logo"
            className="dark"
            width={150}
            height={150}
            style={{ width: 'auto', height: 'auto' }}
            priority
          />
        </div>
        <div className="flex flex-col justify-center rounded-lg bg-gray-50 px-10 py-20 w-full h-full m-1 basis-8/12  text-center">
          <ul role="list" className="p-6 divide-y divide-slate-200 space-y-4">
            <li>
              <strong>Welcome</strong>
              <p>Take a bite out of life 🍪, have a snack 🥗</p>
            </li>
            <li>
              <LoginButton provider="Facebook" className="bg-sky-500 hover:bg-sky-700 px-5 py-2 text-sm leading-5 rounded-full font-semibold text-white" />
            </li>
          </ul>
        </div>
      </div>
    </main >
  );
}

