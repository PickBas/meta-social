#!/bin/bash

sed -i s/community = models.ForeignKey(to='community.Community', on_delete=models.CASCADE, null=True)/community = models.ForeignKey(to='community.models.Community', on_delete=models.CASCADE, null=True) meta_social/apps/post/models.py

sed -i s/owner_community = models.ForeignKey(to='community.Community', on_delete=models.CASCADE, null=True, related_name='owner_community')/owner_community = models.ForeignKey(to='community.models.Community', on_delete=models.CASCADE, null=True, related_name='owner_community') meta_social/apps/post/models.py

# run pylint
pylint $(python ./pylint_runner.py) --load-plugins pylint_django | tee pylint.txt

# get badge
mkdir public
score=$(sed -n 's/^Your code has been rated at \([-0-9.]*\)\/.*/\1/p' pylint.txt)
anybadge --value=$score --file=public/pylint.svg pylint
echo "Pylint score was $score"

exit 0
