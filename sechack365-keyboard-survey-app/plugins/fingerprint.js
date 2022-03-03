import FingerprintJS from '@fingerprintjs/fingerprintjs'

// Initialize an agent at application startup.
const fingerprint = FingerprintJS.load()

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export default ({ app }, inject) => {
  // Inject $hello(msg) in Vue, context and store.
  inject('fingerprint', fingerprint)
}
