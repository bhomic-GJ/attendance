#! /usr/bin/env bash

sql() {
    echo "$1"
    mysql -e "use attendance; $1"
    echo ""
}

describe() {
    sql "describe \`${1^^}\`"
}

view() {
    sql "select * from \`${1^^}\` $2"
}

# sql "insert into \`GROUP\`(Name, OID, Creator) values ('A', '61c8d38d-2c9e-4197-998e-0ef01eb3488c', 'f47da81f-f94a-4dcb-8fa6-ca61ccc736df')"
# for i in {A..I}; do
#     sql "insert into \`GROUP\` values ('$i', '61c8d38d-2c9e-4197-998e-0ef01eb3488c', 'f47da81f-f94a-4dcb-8fa6-ca61ccc736df', NOW())"
# done

# sql "insert into GROUP_HIERARCHY values ('C', '61c8d38d-2c9e-4197-998e-0ef01eb3488c', 'A')"
# sql "insert into GROUP_HIERARCHY values ('D', '61c8d38d-2c9e-4197-998e-0ef01eb3488c', 'A')"
# sql "insert into GROUP_HIERARCHY values ('E', '61c8d38d-2c9e-4197-998e-0ef01eb3488c', 'B')"
# sql "insert into GROUP_HIERARCHY values ('F', '61c8d38d-2c9e-4197-998e-0ef01eb3488c', 'B')"
# sql "insert into GROUP_HIERARCHY values ('G', '61c8d38d-2c9e-4197-998e-0ef01eb3488c', 'C')"
# sql "insert into GROUP_HIERARCHY values ('H', '61c8d38d-2c9e-4197-998e-0ef01eb3488c', 'C')"
# sql "insert into GROUP_HIERARCHY values ('I', '61c8d38d-2c9e-4197-998e-0ef01eb3488c', 'E')"

# sql "describe \`GROUP\`"
# sql "describe \`USER\`"

# sql "select * from \`GROUP\`"
# sql "select * from \`USER\`"
# sql "select * from \`ORGANIZATION\`"
# sql "select * from \`GROUP_HIERARCHY\`"

# sql "delete from \`GROUP_HIERARCHY\`"
# sql "delete from \`GROUP\`"
# sql "alter table \`GROUP\` modify Creation_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP"

# sql "select Name, OID, Parent from \`GROUP\` NATURAL LEFT OUTER JOIN GROUP_HIERARCHY"

# sql "
#     SELECT \`GROUP\`.\`Name\`, \`GROUP\`.\`OID\`, \`GROUP_HIERARCHY\`.\`Parent\` 
#     FROM \`GROUP\` LEFT OUTER JOIN \`GROUP_HIERARCHY\` ON \`GROUP_HIERARCHY\`.\`OID\` = \`GROUP\`.\`OID\` AND \`GROUP_HIERARCHY\`.\`Name\` = \`GROUP\`.\`Name\` 
#     WHERE \`GROUP_HIERARCHY\`.\`Parent\` IS NULL AND \`GROUP\`.\`OID\` = '61c8d38d-2c9e-4197-998e-0ef01eb3488c' ORDER BY \`GROUP_HIERARCHY\`.\`Name\` ASC
# "

# curl "http://localhost:5000/api/users/create" -d "name=DEF&username=DEF&password=1234"
# curl "http://localhost:5000/api/users/login" -d "username=user1&password=1234"
# curl "http://localhost:5000/api/users/view" -H "Authorization: Bearer REVGOo8uymUGVE9Vo4XGK3S4Two6wUlWYgpSEe2WEk43niBwBA=="

# sql "INSERT INTO MEMBERSHIP() VALUES ('')"

# curl "http://localhost:5000/api/group/61c8d38d-2c9e-4197-998e-0ef01eb3488c/view/members"
# curl "http://localhost:5000/api/group/61c8d38d-2c9e-4197-998e-0ef01eb3488c/A/view/members"

# curl "http://localhost:5000/api/group/leave" -d "OID=61c8d38d-2c9e-4197-998e-0ef01eb3488c&group=I" -H "Authorization: Bearer VTE6Pfwf6F1XQMW6fM1G4FXXajqHlbM2CmkR7YvXTjeeIHAE"

# arr=('U1' 'U2' 'U3' 'U4')
# for user in "${arr[@]}"; do
#     curl "http://localhost:5000/api/users/create" -d "name=$user&username=$user&password=1234&organization=61c8d38d-2c9e-4197-998e-0ef01eb3488c"
# done

# sql "
#      SELECT \`USER\`.\`Name\`, OID, OJoin_Date FROM \`USER\` 
#         WHERE \`USER\`.\`OID\` = '61c8d38d-2c9e-4197-998e-0ef01eb3488c' AND NOT ( EXISTS (SELECT \`MEMBERSHIP\`.\`ID\` 
#     FROM \`MEMBERSHIP\` WHERE \`MEMBERSHIP\`.\`OID\` = \`USER\`.\`OID\`) )
# "

# describe "schedule";
# describe "active_schedule";

# describe "schedule";
# sql "select datediff('2022-07-28', '2022-07-26')"
# view "organization";
# view "admin";
# view "user" "where username='user1'"
# sql "insert into ADMIN values('93c5f28f-e5ac-4aba-97fc-ad0cfbf7088a')"

# sql "DELETE FROM MEMBERSHIP"

# view "user" "where username = 'DEF'";
# describe "attendance";

view "ORGANIZATION";
view 'schedule';
describe 'active_schedule';
describe 'attendance';

# sql "select * from SCHEDULE where mod(datediff('2022-08-03', Commencement_Date), Frequency) = 0"

# curl "http://localhost:5000/api/group/61c8d38d-2c9e-4197-998e-0ef01eb3488c/view/members"
# curl "http://localhost:5000/api/schedule/create" -d "group=A&start_time=09:00:00&end_time=11:00:00&start_date=2022-07-27&title=EV1&status=1&frequency=7" -H "Authorization: Bearer dXNlcjE65Tq3cJPVQU2XUjIrt41rmjojWkXYDLQR7btYRrPRrRwy3S8WjjDGMotJow"

# sql "UPDATE USER SET OID='61c8d38d-2c9e-4197-998e-0ef01eb3488c', OJoin_Date=NOW() WHERE Username='DEF'"