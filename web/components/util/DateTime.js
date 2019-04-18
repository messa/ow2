import React from 'react'

export default class DateTime extends React.Component {

  state = {
    ago: null
  }

  componentDidMount() {
    this.updateAgo()
    if (this.props.updateAgo) {
      this.updateAgoIntervalId = setInterval(this.updateAgo, 3 * 1000)
    }
  }

  componentWillUnmount() {
    if (this.updateAgoIntervalId) {
      clearInterval(this.updateAgoIntervalId)
    }
  }

  updateAgo = () => {
    const dt = new Date(this.props.value) * 0.001
    const now = new Date() * 0.001
    const totalSeconds = Math.floor(now - dt)
    if (totalSeconds < 60) {
      this.setState({ ago: `${totalSeconds} s` })
    } else if (totalSeconds < 3600) {
      const minutes = Math.floor(totalSeconds / 60)
      const seconds = totalSeconds % 60
      this.setState({ ago: `${minutes} m ${seconds} s` })
    } else if (totalSeconds < 86400) {
      const hours = Math.floor(totalSeconds / 3600)
      const minutes = Math.floor((totalSeconds % 3600) / 60)
      this.setState({ ago: `${hours} h ${minutes} m` })
    } else {
      const days = Math.floor(totalSeconds / 86400)
      const hours = Math.floor((totalSeconds % 86400) / 3600)
      this.setState({ ago: `${days} d ${hours} h` })
    }
  }

  render() {
    const { value } = this.props
    const { ago } = this.state
    const dt = new Date(value)
    return (
      <span className='DateTime' title={dt.toISOString()}>
        {dt.toISOString().slice(0, 19).replace('T', ' ')}
        {ago && <small style={{ marginLeft: 6 }}>(<b>{ago}</b> ago)</small>}
      </span>
    )
  }

}
