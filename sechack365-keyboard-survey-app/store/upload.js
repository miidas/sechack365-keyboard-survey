export const state = () => ({
  upload_id: '',
  view_key: '',
})

export const mutations = {
  save(state, obj) {
    state.upload_id = obj.upload_id
    state.view_key = obj.view_key
  },
}
