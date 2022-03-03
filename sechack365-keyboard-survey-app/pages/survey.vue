<template>
  <v-row justify="center" align="center">
    <v-col cols="12" sm="8" md="6">
      <div class="text-center pb-3">
        <SH365Logo />
      </div>
      <v-card>
        <v-card-title class="title">調査</v-card-title>
        <v-card-text>
          <div class="text-right">
            <p>データ数: {{ current_text_pos }} / {{ texts.length }}</p>
          </div>
          <div class="text-center pb-3">
            <h2 v-html="current_text.html"></h2>
          </div>
          <v-text-field
            v-model="user_text"
            @input="textFieldEvent"
            @keypress="textFieldEvent"
            @keydown="textFieldEvent"
            @keyup="textFieldEvent"
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-btn active-class="no-active" color="primary" nuxt to="/select">
            戻る
          </v-btn>
          <v-spacer />
          <v-btn
            active-class="no-active"
            color="primary"
            @click.stop="dialog = true"
          >
            送信
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-col>

    <v-dialog v-model="dialog" max-width="400">
      <v-card>
        <v-card-title class="text-h5">データの送信</v-card-title>
        <v-card-text>
          キーボードの入力操作とマイク音声をサーバーに送信します
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="dialog = false">
            拒否
          </v-btn>
          <v-btn color="blue darken-1" text @click="sendData"> 承認 </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="dialog3" max-width="400">
      <v-card>
        <v-card-title class="text-h5">入力終了</v-card-title>
        <v-card-text>
          全てのテキストを使い切りました。<br />
          送信ボタンを押して調査を終了してください。
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="dialog3 = false">
            OK
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="dialog2" persistent max-width="400">
      <v-card>
        <v-card-title class="text-h5">データ送信中</v-card-title>
        <v-card-text>
          <p>完了までお待ちください... ({{ uploadPercentage }}%)</p>
          <v-progress-linear :value="uploadPercentage"></v-progress-linear>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<script>
export default {
  name: 'Survey',
  data() {
    return {
      current_text: '読み込み中...',
      current_text_pos: 0,
      texts: [],
      user_text: '',
      user_log: [],
      user_key_events: [],
      dialog: false,
      dialog2: false,
      dialog3: false,
      uploadPercentage: 0,
      mic_selected_device: '',
      mediaRecorder: null,
      audioData: null,
      audio_info: {},
      audio_chunks: [],
      fingerprints: {},
    }
  },
  computed: {
    wizard_step() {
      return this.$store.state.wizard.step
    },
    questions() {
      return this.$store.state.question.questions
    },
    mic_devices() {
      return this.$store.state.device.devices
    },
    selected_device() {
      return this.$store.state.device.selected_device
    },
    select_mode() {
      return this.$store.state.select_mode.input_mode
    },
  },
  mounted() {
    this.checkWizardStep()
    this.updateWizardStep()
    this.loadDataFromStore()
    this.loadText()
    this.startRecording()
    this.collectFingerprints()
  },
  methods: {
    checkWizardStep() {
      if (this.wizard_step < 4) {
        this.$router.push({ name: 'index' })
      }
    },
    updateWizardStep() {
      this.$store.commit('wizard/save', Math.max(this.wizard_step, 5))
    },
    loadDataFromStore() {
      this.mic_selected_device = this.selected_device
    },
    async loadText() {
      // Load texts using axios
      const txtPath = await this.$axios.$get(
        '/api/v1/txt?mode=' + this.select_mode
      )
      // let texts = await this.$axios.$get('/text/ss/ss_01.json')
      let texts = await this.$axios.$get(txtPath.file)
      texts = texts.sort(() => 0.5 - Math.random())

      this.current_text = texts[0]
      this.texts = texts
    },
    collectFingerprints() {
      const self = this
      this.$fingerprint
        .then((fp) => fp.get())
        .then((result) => {
          delete result.components.canvas
          self.fingerprints = {
            user_agent: navigator.userAgent,
            mic_interface: self.mic_devices.filter(
              (mic) => mic.deviceId === self.mic_selected_device
            )[0].label,
            fingerprint: result,
          }
        })
    },
    textFieldEvent(e) {
      if (typeof e === 'object') {
        // KeyboardEvent
        // console.log(e)
        if (e.type === 'keydown') {
          //  && e.key === 'Process'
          const logObj = {
            event_type: e.type,
            key: e.key,
            code: e.code,
            composing: e.isComposing,
            timestamp: e.timeStamp,
          }

          this.user_key_events.push(logObj)
        } else if (e.type === 'keypress') {
          const logObj = {
            event_type: e.type,
            key: e.key,
            composing: e.isComposing,
            timestamp: e.timeStamp,
          }

          this.user_key_events.push(logObj)

          if (e.key === 'Enter' && this.user_text !== '') {
            const gLogObj = {
              text: this.current_text.text,
              user_text: this.user_text,
              key_events: this.user_key_events,
            }

            this.user_log.push(gLogObj)

            // Reset
            this.user_text = ''
            this.user_key_events = []

            // Check if text is available
            if (this.current_text_pos + 1 >= this.texts.length) {
              this.current_text_pos++
              this.current_text = '送信ボタンを押してください...'
              this.dialog3 = true
              return
            }

            // Display next text
            this.current_text_pos++
            this.current_text = this.texts[this.current_text_pos]
          }
        }
      } else if (typeof e === 'string') {
        // Input string
        // https://developer.mozilla.org/en-US/docs/Web/API/Event/timeStamp
        // https://developer.mozilla.org/en-US/docs/Web/API/DOMHighResTimeStamp
        const timeStamp = performance.now()
        const logObj = {
          event_type: 'input',
          input_str: e,
          timestamp: timeStamp,
        }

        this.user_key_events.push(logObj)
      }
    },
    sendData() {
      this.dialog = false
      this.dialog2 = true

      const self = this
      this.stopRecording(function () {
        const formData = new FormData()
        formData.append('questions', JSON.stringify(self.questions))
        formData.append('user_log', JSON.stringify(self.user_log))
        formData.append('audio_info', JSON.stringify(self.audio_info))
        formData.append('audio_data', self.audioData)
        formData.append('fingerprints', JSON.stringify(self.fingerprints))

        self.$axios
          .post('/api/v1/upload', formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
            onUploadProgress(e) {
              self.uploadPercentage = parseInt(
                Math.round((e.loaded / e.total) * 100)
              )
            },
          })
          .then(function (res) {
            self.$store.commit('upload/save', res.data)
            self.$router.push({ name: 'finished' })
          })
          .catch(function () {
            console.log('Something happened while uploading files!?') // why...
          })
      })
    },
    startRecording() {
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
          const options = {
            audioBitsPerSecond: 128000,
            mimeType: 'audio/webm;codecs=opus',
          }
          self.mediaRecorder = new MediaRecorder(stream, options)

          self.mediaRecorder.ondataavailable = function (e) {
            self.audio_chunks.push(e.data)
          }
          self.mediaRecorder.onstart = function () {
            const timeStamp = performance.now()
            self.audio_info = { start_timestamp: timeStamp }
          }
          self.mediaRecorder.start()
        },
        function (err) {
          console.log('navigator.getUserMedia error: ', err.message, err.name)
        }
      )
    },
    stopRecording(callback) {
      const self = this
      this.mediaRecorder.onstop = function () {
        const blob = new Blob(self.audio_chunks, {
          type: 'audio/webm;codecs=opus',
        })

        const reader = new FileReader()
        reader.readAsDataURL(blob)
        reader.onload = function (e) {
          self.audioData = String(e.target.result)

          // Close all stream
          self.mediaRecorder.stream.getTracks().forEach((track) => track.stop())
          callback()
        }
      }
      this.mediaRecorder.stop()
    },
  },
}
</script>
