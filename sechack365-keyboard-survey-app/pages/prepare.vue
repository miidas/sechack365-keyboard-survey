<template>
  <v-row justify="center" align="center">
    <v-col cols="12" sm="8" md="6">
      <div class="text-center pb-3">
        <SH365Logo />
      </div>

      <v-alert
        v-if="mic_state === 'denied'"
        border="left"
        colored-border
        type="error"
        elevation="2"
      >
        マイクへのアクセスがブロックされています<br />
        詳しくは<a
          href="https://support.google.com/chrome/answer/2693767"
          target="_blank"
          >こちら</a
        >をご覧ください
      </v-alert>

      <v-card>
        <v-card-title class="title"> 準備 </v-card-title>
        <v-card-text>
          <div class="text-center">
            <img
              class="MicPromptImg"
              alt="Microphone Prompt"
              src="/mic_prompt.png"
            />
          </div>
          <p>
            マイクの使用を許可し、下記のデバイス一覧から使用するマイクを選択してください<br />
          </p>

          <v-row align="center" justify="center" class="pt-3">
            <v-col class="d-flex" cols="12" sm="6">
              <v-select
                v-model="mic_selected_device"
                :items="mic_devices"
                item-text="label"
                item-value="deviceId"
                label="使用するマイク"
                :disabled="mic_state !== 'granted'"
                outlined
                @change="updateSelectedDevice"
              ></v-select>
            </v-col>
          </v-row>

          <p>
            必要であれば、以下の"マイクチェック"をクリックし、正しく録音されていることを確認してください<br />
            クリック後3秒間録音し、その後音声の再生を行います
          </p>

          <v-row align="center" justify="center" class="pb-10 pt-3">
            <v-btn
              tile
              color="success"
              :disabled="mic_state !== 'granted' || !mic_ready"
              @click="checkMicrophone"
            >
              <v-icon left> mdi-microphone </v-icon>
              マイクチェック
            </v-btn>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-btn active-class="no-active" color="primary" nuxt to="/question">
            戻る
          </v-btn>
          <v-spacer />
          <v-btn
            active-class="no-active"
            color="primary"
            :disabled="mic_state !== 'granted'"
            nuxt
            to="/select"
          >
            次へ
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
import SH365Logo from '~/components/SH365Logo'

export default {
  name: 'Prepare',
  components: {
    SH365Logo,
  },
  data() {
    return {
      mic_state: '',
      mic_devices: [],
      mic_selected_device: '',
      mic_ready: true,
    }
  },
  computed: {
    wizard_step() {
      return this.$store.state.wizard.step
    },
    devices() {
      return this.$store.state.device.devices
    },
    selected_device() {
      return this.$store.state.device.selected_device
    },
  },
  mounted() {
    this.checkWizardStep()
    this.updateWizardStep()
    this.loadDataFromStore()
    this.queryPermission()
  },
  methods: {
    checkWizardStep() {
      if (this.wizard_step < 2) {
        this.$router.push({ name: 'index' })
      }
    },
    updateWizardStep() {
      this.$store.commit('wizard/save', Math.max(this.wizard_step, 3))
    },
    loadDataFromStore() {
      this.mic_devices = this.devices
      this.mic_selected_device = this.selected_device
    },
    queryPermission() {
      const self = this
      navigator.permissions.query({ name: 'microphone' }).then(function (ret) {
        self.mic_state = ret.state // granted, denied, prompt
        if (ret.state === 'prompt') {
          // Prompt the user to authorize access to the microphone
          navigator.getUserMedia(
            { audio: true },
            function (stream) {
              // Close all stream
              stream.getTracks().forEach((track) => track.stop())
            },
            function () {}
          )
          ret.onchange = function () {
            self.mic_state = this.state
            self.enumerateMicrophones()
          }
        } else if (ret.state === 'granted') {
          self.enumerateMicrophones()
        }
      })
    },
    enumerateMicrophones() {
      const self = this
      navigator.mediaDevices
        .enumerateDevices()
        .then(function (devices) {
          const audioInputDevices = []
          for (let i = 0; i !== devices.length; ++i) {
            const device = devices[i]
            if (device.kind === 'audioinput') {
              audioInputDevices.push(device)
            }
          }
          if (
            self.mic_devices.length !== 0 &&
            self.mic_devices.length === audioInputDevices.length
          )
            return
          self.mic_devices = audioInputDevices
          self.mic_selected_device = audioInputDevices[0].deviceId
          self.$store.commit('device/saveDevices', self.mic_devices)
          self.$store.commit(
            'device/saveSelectedDevice',
            self.mic_selected_device
          )
        })
        .catch(function (err) {
          console.log(
            'navigator.mediaDevices.enumerateDevices error: ',
            err.message,
            err.name
          )
        })
    },
    updateSelectedDevice(device) {
      this.$store.commit('device/saveSelectedDevice', device)
    },
    checkMicrophone() {
      const self = this
      navigator.getUserMedia(
        {
          audio: {
            deviceId: this.mic_selected_device,
            echoCancellation: false,
            autoGainControl: false,
            noiseCancellation: false,
          },
        },
        function (stream) {
          self.mic_ready = false
          let chunks = []

          const options = {
            audioBitsPerSecond: 128000,
            mimeType: 'audio/webm;codecs=opus',
          }
          const mediaRecorder = new MediaRecorder(stream, options)

          mediaRecorder.ondataavailable = function (e) {
            chunks.push(e.data)
          }
          mediaRecorder.onstop = function () {
            const blob = new Blob(chunks, { type: 'audio/webm;codecs=opus' })
            const audioUrl = window.URL.createObjectURL(blob)

            // Clear chunks
            chunks = []
            // Close all stream
            stream.getTracks().forEach((track) => track.stop())

            const audio = new Audio(audioUrl)
            audio.addEventListener('ended', function () {
              self.mic_ready = true
            })
            audio.play()
          }

          mediaRecorder.start()

          // Record for 3 seconds
          setTimeout(function () {
            mediaRecorder.stop()
          }, 3000)
        },
        function (err) {
          console.log('navigator.getUserMedia error: ', err.message, err.name)
        }
      )
    },
  },
}
</script>

<style lang="scss" scoped>
.MicPromptImg {
  height: 60%;
  width: auto;
}
</style>
