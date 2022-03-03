export const state = () => ({
  devices: [],
  selected_device: '',
})

export const mutations = {
  saveDevices(state, obj) {
    state.devices = obj
  },
  saveSelectedDevice(state, device) {
    state.selected_device = device
  },
}
