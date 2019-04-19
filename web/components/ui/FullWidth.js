import React from 'react'

export default class FullWidth extends React.Component {

  state = {
    height: 40,
  }

  constructor(props) {
    super(props)
    this.contentRef = React.createRef()
  }

  componentDidMount() {
    this.updateHeight()
    this.intervalId = setInterval(this.updateHeight, 500)
  }

  componentWillUnmount() {
    if (this.intervalId) {
      clearInterval(this.intervalId)
    }
  }

  updateHeight = () => {
    const height = this.contentRef.current.offsetHeight
    if (height !== this.state.height) {
      this.setState({ height })
    }
  }

  render() {
    const { children } = this.props
    const { height } = this.state
    return (
      <div
        style={{
          height,
        }}
      >
        <div
          ref={this.contentRef}
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
          }}
        >
          {children}
        </div>
      </div>
    )
  }

}
