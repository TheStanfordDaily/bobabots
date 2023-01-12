const MAXIMUM_NTRIALS = 20
const MINIMUM_SLEEP_MS = 500
const MAXIMUM_SLEEP_MS = 2000
const CLEAR_ID = "remove-filter193"
const FILTER_ID = "Filter193"
const PERSON_DATA_CLASS = "person__data__main"

function randomDuration(minimum, maximum) {
    return Math.floor(Math.random() * maximum) + minimum
}

async function sleep(time) {
    return new Promise(resolve => setTimeout(resolve, time))
}

async function randomSleep() {
    return await sleep(randomDuration(MINIMUM_SLEEP_MS, MAXIMUM_SLEEP_MS))
}


class InfiniteScroll {
    constructor(department) {
        console.log("Initializing infinite scroll...")
        this.department = department
        this.resetFilter()
        this.simulateKeyboardEvent(FILTER_ID, department)
        this.currentScrollHeight = 0
        this.numberOfScrolls = 0
        this.numberOfTrials = 0
    }

    async exhaust() {
        this.currentScrollHeight = document.body.scrollHeight
        window.scrollTo(0, this.currentScrollHeight)
        await randomSleep()

        if (this.currentScrollHeight === document.body.scrollHeight) {
            this.numberOfTrials++
            const attemptsRemaining = MAXIMUM_NTRIALS - this.numberOfTrials
            let updateMessage = "Bottom of scroll window detected. Will check for additional content "
            updateMessage += attemptsRemaining.toString() + " more time" + (attemptsRemaining === 1 ? "" : "s") + "..."
            console.log(updateMessage)
        } else {
            this.numberOfTrials = 0
            this.numberOfScrolls++
            console.log(`Scroll ${this.numberOfScrolls} was successful!`)
            if (!(this.ranOver() || this.numberOfTrials > MAXIMUM_NTRIALS)) {
                this.exhaust()
            } else {
                this.summarize()
            }
        }
    }

    summarize() {
        console.log("We should be at the bottom of the infinite scroll now. Done!")
        console.log(`Loaded ${this.numberOfScrolls} pages for ${this.department}.`)
        console.log(this.href='data:text/htmlcharset=UTF-8,'+encodeURIComponent(document.documentElement.outerHTML))
    }

    ranOver() {
        const elements = Array.prototype.slice.call(document.getElementsByClassName(PERSON_DATA_CLASS))
        return elements.length > 0 && !elements.every(element => element.innerText.includes(this.department))
    }

    simulateKeyboardEvent(id, text) {
        const input = document.getElementById(id)
        const event = new Event("input", { bubbles: true })
        input.value += text
        input.dispatchEvent(event)
    }

    resetFilter() {
        window.scrollTo(0, 0)
        document.getElementById(CLEAR_ID).click()
    }
}

const infiniteScroll = new InfiniteScroll("English")
infiniteScroll.exhaust()