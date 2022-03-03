<template>
  <v-row justify="center" align="center">
    <v-col cols="12" sm="8" md="6">
      <div class="text-center pb-3">
        <SH365Logo />
      </div>
      <v-card>
        <v-card-title class="title">完了</v-card-title>
        <v-card-text>
          <p>
            調査にご協力いただきありがとうございました。<br />
            あなたの提出IDは <code>{{ upload_id }}</code> です。<br />
            提出ファイルの確認は
            <a :href="'/view?action=get&uuid=' + upload_id + '&key=' + view_key"
              >こちら</a
            >
          </p>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
export default {
  name: 'Finished',
  computed: {
    wizard_step() {
      return this.$store.state.wizard.step
    },
    upload_id() {
      return this.$store.state.upload.upload_id
    },
    view_key() {
      return this.$store.state.upload.view_key
    },
  },
  mounted() {
    this.checkWizardStep()
    this.updateWizardStep()
  },
  methods: {
    checkWizardStep() {
      if (this.wizard_step !== 5) {
        this.$router.push({ name: 'index' })
      }
    },
    updateWizardStep() {
      this.$store.commit('wizard/save', 0)
    },
  },
}
</script>

<style lang="scss" scoped>
.v-application code {
  color: #dc143c;
}
</style>
