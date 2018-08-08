# How to contribute

I'm really glad you're reading this, because we need volunteer developers to help this project come to fruition.

If you haven't already, come find us in Slack. You can request an invite to our channel by emailing bryce [at] bridgetownint.com
We want you working on things you're excited about.

Here are some important resources:

  * [Trello, where our roadmap lives](https://trello.com/b/JbO24cjt/constituent-software)
  * Slack is where our conversations take place
  * You can file a bug using [Github issues](https://github.com/PocketLobby/sausage/issues)


## Summary of Workflow

Trello is our roadmap. The cards in the TODO list are sorted by priority. When choosing the next story to work on, pick from the top of the TODO list.

Make frequent commits and submit a WIP PR when you have the approach that you've developed figured out. The code doesn't
have to be production ready. We like to get feedback early and often and the team knows that WIP PRs aren't perfect.

Once your PR is ready for final review, remove the WIP from the PR title and ping the technology channel in Slack that
your code is ready for review. Once you get a "LGTM" or :+1: on the PR, merge it into master yourself.

## Testing

All code submitted for PR should have sufficient test coverage. Sufficient is up to the interpretation of the developers
and code reviewers but generally includes at least unit testing.

## Commits

Always write a clear log message for your commits. Start with a summary line, a blank line and then the _why_ and _what_
of the commit. [Chris Beams has a great article about this](https://chris.beams.io/posts/git-commit/)

Example:

    > The subject of a commit
    > 
    > A paragraph describing what and why code was changed
    >   * Maybe a bullet or two
    
Git branches should have the naming convention of `<your initials>/<summary-of-work>` i.e. `bam/enhanced-tally-mails`

## Coding conventions

As much as possible, we follow the PEP8 conventions established by the Python community. Future versions of this project
will include a linter and/or official style guide.

Thanks and happy contributing,

Bryce, Pocket Lobby
