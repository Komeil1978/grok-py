echo 'Doing a clean build of docs ...'
make clean
make html
echo 'Done.'

read -p "Please check for build errors. Would you like to continue? [y/n]: " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then

    echo ''
    echo 'Copying latest build of docs to numenta.github.com repo ...'
    cp -R _build/html/* ~/nta/numenta.github.com/grok-py/
    echo 'Done.'

    echo 'Committing changes to github.numenta.com repo ...'
    cd ~/nta/numenta.github.com/grok-py/
    git add *
    git commit -m 'Update Python Docs' .
    echo 'Done.'

    echo 'Pushing changes to from numenta.github.com to gitmo ...'
    git push origin master
    echo 'Done.'

    read -p "Publish these changes? (This will go live immediately.)[y/n]: " -n 1 -r
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
	echo ''
	echo 'Pushing changes from numenta.github.com to github ...'
	git push github
	echo 'Done.'
    fi
fi


