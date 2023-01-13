const MAXIMUM_NTRIALS = 5
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

// Source: http://bgrins.github.io/devtools-snippets/#console-save

(function(console){

    console.save = function(data, filename){
    
        if(!data) {
            console.error('Console.save: No data')
            return;
        }
    
        if(!filename) filename = 'console.json'
    
        if(typeof data === "object"){
            data = JSON.stringify(data, undefined, 4)
        }
    
        var blob = new Blob([data], {type: 'text/json'}),
            e    = document.createEvent('MouseEvents'),
            a    = document.createElement('a')
    
        a.download = filename
        a.href = window.URL.createObjectURL(blob)
        a.dataset.downloadurl =  ['text/json', a.download, a.href].join(':')
        e.initMouseEvent('click', true, false, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null)
        a.dispatchEvent(e)
     }
})(console)


class InfiniteScroll {
    constructor(department) {
        console.log("Initializing infinite scroll...")
        this.resetFilter()
        this.simulateKeyboardEvent(FILTER_ID, department)
        this.department = department
        this.currentScrollHeight = 0
        this.numberOfScrolls = 0
        this.numberOfTrials = 0
    }

    async exhaust() {
        if (this.numberOfTrials > MAXIMUM_NTRIALS) {
            this.summarize()
            return
        }

        this.currentScrollHeight = document.body.scrollHeight
        window.scrollTo(0, this.currentScrollHeight)
        await randomSleep()
        
        if (this.currentScrollHeight === document.body.scrollHeight) {
            this.numberOfTrials++
            const attemptsRemaining = MAXIMUM_NTRIALS - this.numberOfTrials
            let updateMessage = "Bottom of scroll window detected. Will check for additional content " + attemptsRemaining.toString() + " more time"
            updateMessage += attemptsRemaining === 1 ? "..." : "s..."
            console.log(updateMessage)
        } else {
            this.numberOfTrials = 0
            this.numberOfScrolls++
            console.log(`Scroll ${this.numberOfScrolls} was successful!`)
        }

        this.entriesRemain() ? await this.exhaust() : this.summarize()
    }

    summarize() {
        console.log("We should be at the bottom of the infinite scroll now. Done!")
        console.log(`Loaded ${this.numberOfScrolls} pages for ${this.department}.`)
        console.save(document.documentElement.outerHTML, `${this.department}.html`)
    }

    entriesRemain() {
        const elements = Array.prototype.slice.call(document.getElementsByClassName(PERSON_DATA_CLASS))
        return elements.every(element => element.innerText.includes(this.department))
    }

    simulateKeyboardEvent(id, text) {
        const input = document.getElementById(id)
        input.value += text
        input.dispatchEvent(new Event("input", { bubbles: true }))
    }

    resetFilter() {
        window.scrollTo(0, 0)
        document.getElementById(CLEAR_ID).click()
    }
}

const departments = ["English", "Music", "History"]

for (let department of departments) {
    const infiniteScroll = new InfiniteScroll(department)
    try {
        await infiniteScroll.exhaust()
    } catch (error) {
        console.log(`Scrolling for ${department} failed: ${error}`)
    }
}